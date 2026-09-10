import contextlib
import io
import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from jw.cli import main
from jw.config import load_data


class CLITests(unittest.TestCase):
    def setUp(self):
        self.workspace = tempfile.TemporaryDirectory()
        self.addCleanup(self.workspace.cleanup)
        self.root = Path(self.workspace.name)
        self.source = self.root / "source.txt"
        self.source.write_text("値は12 N。", encoding="utf-8")

    def call(self, *args):
        output, error = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(output), contextlib.redirect_stderr(error):
            code = main(list(map(str, args)))
        return code, output.getvalue(), error.getvalue()

    def test_audit_compare_exit_status(self):
        code, output, _ = self.call("audit", self.source, "--json")
        self.assertEqual(code, 0)
        self.assertEqual(json.loads(output)["status"], "PASS")
        target = self.root / "target.txt"
        target.write_text("値は21 N。", encoding="utf-8")
        code, output, _ = self.call("compare", self.source, target, "--json")
        self.assertEqual(code, 1)
        self.assertEqual(json.loads(output)["status"], "FAIL")
        self.assertNotIn("21 N", output)

    def test_no_overwrite_and_explicit_output(self):
        code, _, _ = self.call("audit", self.source, "--report", self.source)
        self.assertEqual(code, 2)
        self.assertEqual(self.source.read_text(encoding="utf-8"), "値は12 N。")
        report = self.root / "report.json"
        self.assertEqual(self.call("audit", self.source, "--json", "--report", report)[0], 0)
        self.assertEqual(self.call("audit", self.source, "--json", "--report", report)[0], 2)

    def test_failed_replay_does_not_create_prose(self):
        responses = self.root / "responses.json"
        responses.write_text(json.dumps([{"edits": [{"sentence_id": 0, "text": "値は99 N。"}]}]), encoding="utf-8")
        output = self.root / "output.txt"
        code, _, _ = self.call("replay", self.source, responses, "--max-revision", 0, "--output", output)
        self.assertEqual(code, 1)
        self.assertFalse(output.exists())
        self.assertEqual(len(list(self.root.iterdir())), 2)

    def test_successful_replay(self):
        responses = self.root / "responses.json"
        responses.write_text('[{"edits": []}]', encoding="utf-8")
        output = self.root / "output.txt"
        self.assertEqual(self.call("replay", self.source, responses, "--output", output)[0], 0)
        self.assertEqual(output.read_bytes(), self.source.read_bytes())

    def test_crlf_count_and_identity_preservation(self):
        self.source.write_bytes("値は12 N。\r\n".encode("utf-8"))
        self.assertEqual(self.call("audit", self.source, "--max-chars", 8)[0], 1)
        self.assertEqual(self.call("audit", self.source, "--max-chars", 8, "--count-mode", "no_newlines")[0], 0)
        responses = self.root / "responses.json"
        responses.write_text('[{"edits": []}]', encoding="utf-8")
        output = self.root / "output.txt"
        self.assertEqual(self.call("replay", self.source, responses, "--output", output)[0], 0)
        self.assertEqual(output.read_bytes(), self.source.read_bytes())

    def test_flat_yaml_and_rejection(self):
        config = self.root / ".jw.yaml"
        config.write_text('genre: technical\nmax_chars: 4\nterms:\n  - "試作材A"\n', encoding="utf-8")
        self.assertEqual(load_data(config)["terms"], ["試作材A"])
        self.assertEqual(self.call("audit", self.source, "--config", config)[0], 1)
        for content in ("max_chars: 2\nmax_chars: 10\n", "x: !!python/object:bad", "max_chars: .nan", "unknown: 1"):
            config.write_text(content, encoding="utf-8")
            self.assertEqual(self.call("audit", self.source, "--config", config)[0], 2)


if __name__ == "__main__":
    unittest.main()
