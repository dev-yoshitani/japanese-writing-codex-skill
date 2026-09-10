import importlib.util
import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from jw.core.report import compare
from jw.contracts import validate, schema


class EvaluationTests(unittest.TestCase):
    def test_fixed_synthetic_benchmark(self):
        spec = importlib.util.spec_from_file_location("benchmark", ROOT / "bench/run.py")
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        result = module.evaluate(ROOT / "bench/datasets")
        self.assertEqual(sum(row["cases"] for row in result["genres"].values()), 120)
        self.assertEqual(result["failed_case_ids"], [])

    def test_golden_report(self):
        source = (ROOT / "examples/source.txt").read_text(encoding="utf-8")
        target = (ROOT / "examples/changed.txt").read_text(encoding="utf-8")
        result = json.loads(json.dumps(compare(source, target)))
        expected = json.loads((ROOT / "tests/golden/changed-report.json").read_text(encoding="utf-8"))
        self.assertEqual(result, expected)
        validate(result, schema("report"))

    def test_schema_implementation_rejects_unsupported_keywords(self):
        with self.assertRaises(ValueError):
            validate({}, {"oneOf": []})


if __name__ == "__main__":
    unittest.main()
