"""Lexical safety checks on authored examples, not a prose-quality evaluation."""
import json
from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from jw.core.report import compare


class WritingExamplesTests(unittest.TestCase):
    def test_authored_candidates_keep_protected_items(self):
        path = Path(__file__).resolve().parents[1] / "examples" / "natural-writing.json"
        for case in json.loads(path.read_text(encoding="utf-8"))["cases"]:
            with self.subTest(case=case["id"]):
                report = compare(case["source"], case["candidate"],
                                 terms=case.get("terms", ()), genre=case["genre"])
                self.assertNotEqual(report["status"], "FAIL", report["findings"])
                self.assertLessEqual(report["metrics"]["edit_ratio"], 1)
                # The engine deliberately does not verify the editorial notes.
                self.assertFalse(report["coverage"]["semantic_verification"])


if __name__ == "__main__":
    unittest.main()
