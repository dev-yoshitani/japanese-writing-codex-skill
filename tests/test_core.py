import json
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from jw.core.align import align
from jw.core.constraints import Constraints, count_characters
from jw.core.extract import extract
from jw.core.lint import lint, RULES
from jw.core.masking import mask, restore
from jw.core.normalize import number_key
from jw.core.report import compare, edit_ratio
from jw.core.segment import segment
from jw.contracts import schema, validate


class CoreTests(unittest.TestCase):
    def test_numeric_equivalence(self):
        for original, revised in (("１，２００ Ｎ", "1200 N"), ("三百 mm", "300 mm"),
                                  ("十二人", "12人"), ("〇五人", "5人"), ("1.5e3 N", "1500 N"),
                                  ("−2.50 MPa", "-2.5 MPa"), ("0.002 N", "2e-3 N")):
            with self.subTest(original=original):
                report = compare("測定値は" + original + "である。", "測定値は" + revised + "である。")
                self.assertNotEqual(report["status"], "FAIL", report["findings"])

    def test_large_numbers_remain_distinct(self):
        self.assertNotEqual(number_key("1234567890123456789012345678901"), number_key("1234567890123456789012345678902"))

    def test_date_and_time(self):
        report = compare("測定は2026年4月3日 09:05。", "測定は2026-04-03 9:05。")
        self.assertNotEqual(report["status"], "FAIL")
        self.assertEqual([f.kind for f in extract("2026年4月3日 09:05")], ["date", "time"])

    def test_unit_and_sign_changes_fail(self):
        for old, new in (("12 m", "12 mm"), ("12 MPa", "12 mPa"), ("-12 N", "12 N"),
                         ("12 m/s^2", "12 m/s"), ("12 N", "21 N"), ("12%", "13%")):
            with self.subTest(old=old, new=new):
                self.assertEqual(compare("値は" + old, "値は" + new)["status"], "FAIL")

    def test_occurrences_and_additions(self):
        original = "値は12 Nと12 Nである。"
        self.assertEqual(sum(f["rule"] == "fact.removed" for f in compare(original, "値は12 Nである。")["findings"]), 1)
        self.assertTrue(any(f["rule"] == "fact.added" for f in compare("試験を行った。", "試験を3回行った。")["findings"]))
        self.assertEqual(compare("入力は10 N。出力は20 N。", "入力は20 N。出力は10 N。")["status"], "FAIL")

    def test_code_math_urls_and_terms(self):
        for old, new, terms in (("式は$σ = F/A$。", "式は$σ = F* A$。", ()),
                                ("値は`a=1`。", "値は`a=2`。", ()),
                                ("資料https://example.org/A。", "資料https://example.org/a。", ()),
                                ("限界荷重を確認。", "終極荷重を確認。", ("限界荷重", "終極荷重")),
                                ("式は$x=K$。", "式は$x=K$。", ())):
            with self.subTest(old=old):
                self.assertEqual(compare(old, new, terms=terms)["status"], "FAIL")
        self.assertEqual(extract("幅は１２ mm。", ())[0].value, "１２ mm")

    def test_lossless_segmentation(self):
        for value in ("", "一文。\r\n次。 ", "値は3.14 mm。https://example.org/a.b を参照。", "`a.b!`を実行。", "段落\n次の段落", "「確認した。」次。"):
            with self.subTest(value=value):
                parts = segment(value)
                self.assertEqual("".join(s.text for s in parts), value)
                for part in parts:
                    self.assertEqual(value[part.start:part.end], part.text)

    def test_alignment_reorder_split_merge(self):
        source = "入力は10 Nである。出力は20 Nである。"
        self.assertNotEqual(compare(source, "出力は20 Nである。入力は10 Nである。")["status"], "FAIL")
        mappings = align(segment("温度は20 Kであり、圧力は30 Paである。"), segment("温度は20 Kである。圧力は30 Paである。"))
        self.assertEqual(mappings[0].target_ids, (0, 1))
        self.assertNotEqual(compare("温度は20 Kであり、圧力は30 Paである。", "温度は20 Kである。圧力は30 Paである。")["status"], "FAIL")
        self.assertEqual(compare("数値は10 N。", "")["status"], "FAIL")

    def test_mask_restores_and_rejects_mutations(self):
        source = "試作材Aは12 N、13 Nに耐えた。"
        masked = mask(source, ("試作材A",))
        self.assertEqual(restore(masked.text, masked), source)
        tokens = [x[0] for x in masked.replacements]
        for corrupted in (masked.text.replace(tokens[0], ""), masked.text + tokens[0],
                          masked.text.replace(tokens[0], "⟦JW0:99⟧"), masked.text.replace(tokens[0], "⟦JWbad⟧"),
                          masked.text.replace(tokens[0], "TMP").replace(tokens[1], tokens[0]).replace("TMP", tokens[1])):
            with self.subTest(corrupted=corrupted):
                with self.assertRaises(ValueError):
                    restore(corrupted, masked)
        with self.assertRaises(ValueError):
            mask("入力⟦JW0:0⟧")

    def test_constraints_and_counts(self):
        # Six Unicode code points; an emoji is one, CR and LF are two.
        self.assertEqual(count_characters("あ😀\r\n い", "all"), 6)
        self.assertEqual(count_characters("あ😀\r\n い", "no_newlines"), 4)
        self.assertEqual(count_characters("あ😀\r\n い", "no_whitespace"), 3)
        self.assertEqual(compare("資料。", constraints=Constraints(max_chars=3))["status"], "PASS")
        self.assertEqual(compare("資料。", constraints=Constraints(max_chars=2))["status"], "FAIL")
        self.assertEqual(compare("資料。", constraints=Constraints(required=("根拠",)))["status"], "FAIL")
        self.assertEqual(compare("資料。", constraints=Constraints(forbidden=("資料",)))["status"], "FAIL")
        for kwargs in ({"min_chars": -1}, {"max_chars": True}, {"max_edit_ratio": float("nan")}, {"min_chars": 2, "max_chars": 1}):
            with self.subTest(kwargs=kwargs), self.assertRaises(ValueError):
                Constraints(**kwargs)

    def test_edit_ratio(self):
        self.assertEqual(edit_ratio("", ""), 0)
        self.assertEqual(edit_ratio("abc", "abc"), 0)
        self.assertEqual(edit_ratio("abc", "abd"), 1 / 3)
        self.assertEqual(edit_ratio("abc", ""), 1)
        self.assertEqual(compare("abc", "def", constraints=Constraints(max_edit_ratio=.2))["status"], "FAIL")

    def test_edit_ratio_different_insert_delete_locations(self):
        # The old larger-document denominator returned 8/5 for this alignment.
        self.assertEqual(edit_ratio("xxxxa", "ayyyy"), 8 / 9)
        report = compare("xxxxa", "ayyyy", constraints=Constraints(max_edit_ratio=1))
        self.assertEqual(report["status"], "WARN")
        self.assertEqual([f["rule"] for f in report["findings"]], ["alignment.uncertain"])
        for source in ("", "ab", "xxxxa", "長い説明。短い判断。", "ab" * 40):
            for target in ("", "ba", "ayyyy", "短い判断。説明を続ける。", "ba" * 40):
                with self.subTest(source=source, target=target):
                    value = edit_ratio(source, target)
                    self.assertGreaterEqual(value, 0)
                    self.assertLessEqual(value, 1)

    def test_ten_lint_rules_are_advisory(self):
        examples = {
            "long_sentence": "文" * 121 + "。",
            "repeated_ending": "結果は妥当である。条件は一定である。評価は必要である。",
            "duplicate_sentence": "確認した。確認した。",
            "emphasis_density": "非常に、極めて、圧倒的に強い。",
            "repeated_triad": "赤、青、白を選ぶ。右、左、上を比べる。",
            "compliance_meta": "ご要望に従って修正した。",
            "repeated_opening": "この実験では測る。この実験では記録した。この実験では比べる。",
            "connective_run": "また、測る。さらに、記録した。そのため、比べる。",
            "verbose_phrase": "計測することが可能である。",
            "mixed_register": "確認するのである。次に測ります。",
        }
        self.assertEqual(set(examples), set(RULES))
        for rule, value in examples.items():
            with self.subTest(rule=rule):
                findings = lint(value)
                self.assertIn("lint." + rule, [f.rule for f in findings])
                self.assertTrue(all(f.severity == "WARN" for f in findings))
        self.assertNotIn("lint.repeated_triad", [f.rule for f in lint("赤、青、白を選ぶ。")])

    def test_report_contract_and_redaction(self):
        report = compare("機密値98765 N。", "機密値87654 N。")
        validate(report, schema("report"))
        rendered = json.dumps(report, ensure_ascii=False)
        self.assertNotIn("98765", rendered)
        self.assertNotIn("機密値", rendered)
        self.assertIn("98765", json.dumps(compare("機密値98765 N。", "機密値87654 N。", include_values=True)))
        self.assertFalse(compare("値は増加する。", "値は減少する。")["coverage"]["semantic_verification"])


if __name__ == "__main__":
    unittest.main()
