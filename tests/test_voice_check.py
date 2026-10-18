"""Checks on review candidates and provenance, not detector performance."""
import contextlib
import importlib.util
import io
import json
from pathlib import Path
import tempfile
import unittest

MODULE = Path(__file__).resolve().parents[1] / "scripts" / "voice_check.py"
spec = importlib.util.spec_from_file_location("voice_check", MODULE)
voice = importlib.util.module_from_spec(spec)
spec.loader.exec_module(voice)


def metadata():
    return {"detector": "Example detector", "measured_at": "2020-01-01T10:00:00+09:00",
            "scope": "full_text", "settings": {"language": "Japanese"},
            "metrics": [{"label": "Displayed label", "value": "Displayed value"}]}


class ReviewTests(unittest.TestCase):
    def kinds(self, before, after):
        return {item["kind"] for item in voice.review(before, after)["checks"]}

    def test_unchanged_prose(self):
        result = voice.review("試作はまだ終わっていない。", "試作はまだ終わっていない。")
        self.assertEqual(result["status"], "CHECKED")
        self.assertFalse(result["meaning_verified"])
        self.assertFalse(result["detector_measured"])

    def test_negation_removed(self):
        self.assertIn("negation", self.kinds("試験で確認していない。", "試験で確認した。"))

    def test_certainty_strengthened(self):
        self.assertIn("certainty", self.kinds("改善する可能性がある。", "改善を実証した。"))

    def test_plan_changed_to_achievement(self):
        self.assertIn("intention", self.kinds("測定する予定です。", "測定しました。"))

    def test_actor_object_swapped(self):
        self.assertIn("roles", self.kinds("田中が佐藤を承認した。", "佐藤が田中を承認した。"))

    def test_code_is_not_style_prose(self):
        self.assertNotIn("negation", self.kinds("`しない`", "`する`"))

    def test_exact_limit_and_crlf(self):
        result = voice.review("あいう。", "あ\r\nいう。", max_chars=4)
        self.assertEqual(result["characters"], 4)
        self.assertNotIn("length", {x["kind"] for x in result["checks"]})
        self.assertIn("length", {x["kind"] for x in voice.review("あ", "あいう", max_chars=2)["checks"]})

    def test_no_raw_prose_in_default_report(self):
        result = voice.review("秘密の原稿です。", "秘密の原稿でした。")
        self.assertNotIn("秘密", json.dumps(result, ensure_ascii=False))
        self.assertIn("秘密", voice.review("秘密です。", "変更です。", include_diff=True)["diff"])

    def test_placeholders_and_empty(self):
        self.assertIn("placeholder", self.kinds("本文", "本文[要確認: 条件]"))
        self.assertIn("empty", self.kinds("本文", ""))

    def test_same_cue_counts_do_not_prove_meaning(self):
        # Deliberately document a blind spot rather than claiming semantic proof.
        before = "Aは確認した。Bは確認していない。"
        after = "Aは確認していない。Bは確認した。"
        result = voice.review(before, after)
        self.assertNotIn("negation", {x["kind"] for x in result["checks"]})
        self.assertFalse(result["meaning_verified"])


class MeasurementTests(unittest.TestCase):
    def test_record_keeps_display_labels_and_self_report(self):
        result = voice.measurement_record("原稿。", metadata())
        self.assertEqual(result["metadata"]["metrics"], metadata()["metrics"])
        self.assertEqual(result["result_source"], "user_reported")
        self.assertFalse(result["measurement_verified"])
        self.assertNotIn("原稿", json.dumps(result, ensure_ascii=False))

    def test_changed_final_invalidates_record(self):
        record = voice.measurement_record("原稿。", metadata())
        self.assertTrue(voice.verify_record("原稿。", record)["input_matches"])
        self.assertEqual(voice.verify_record("原稿。\n", record)["status"], "STALE")

    def test_rejects_missing_conditions_and_naive_time(self):
        for key, value in (("scope", "excerpt"), ("measured_at", "2020-01-01T10:00:00"),
                           ("settings", "unknown"), ("metrics", []),
                           ("measured_at", "9999-01-01T00:00:00Z")):
            with self.subTest(key=key, value=value):
                data = metadata()
                data[key] = value
                with self.assertRaises(ValueError):
                    voice.measurement_record("原稿", data)

    def test_rejects_fabricated_verified_provenance(self):
        result = voice.measurement_record("原稿", metadata())
        result["measurement_verified"] = True
        with self.assertRaises(ValueError):
            voice.verify_record("原稿", result)

    def test_cli_record_verify_and_no_overwrite(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            text, supplied, record = root / "draft.txt", root / "result.json", root / "record.json"
            text.write_bytes("原稿。\r\n".encode("utf-8"))
            supplied.write_text(json.dumps(metadata()), encoding="utf-8")
            with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
                args = ["record", str(text), "--result", str(supplied), "--output", str(record)]
                self.assertEqual(voice.main(args), 0)
                saved = record.read_bytes()
                self.assertEqual(voice.main(args), 2)
                self.assertEqual(record.read_bytes(), saved)
                self.assertEqual(voice.main(["verify", str(text), "--record", str(record)]), 0)
                text.write_bytes("原稿。\n".encode("utf-8"))
                self.assertEqual(voice.main(["verify", str(text), "--record", str(record)]), 3)


if __name__ == "__main__":
    unittest.main()
