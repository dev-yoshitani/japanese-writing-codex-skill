import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from jw.core.extract import extract
from jw.core.report import compare


class NumericRegressionTests(unittest.TestCase):
    def test_200_magnitude_and_sign_mutations(self):
        for number in range(-100, 100):
            source = f"測定値は{number} Nである。"
            target = f"測定値は{number + 1} Nである。"
            with self.subTest(number=number):
                self.assertEqual(compare(source, target)["status"], "FAIL")

    def test_100_width_normalizations(self):
        table = str.maketrans("0123456789", "０１２３４５６７８９")
        for number in range(100):
            source = f"測定値は{str(number).translate(table)} Nである。"
            target = f"測定値は{number} Nである。"
            with self.subTest(number=number):
                self.assertNotEqual(compare(source, target)["status"], "FAIL")

    def test_generic_ascii_units_and_large_exponents(self):
        self.assertEqual(compare("長さは12 ft。", "長さは12 yd。")["status"], "FAIL")
        self.assertEqual(extract("1e999999999")[0].kind, "number")
        self.assertEqual(compare("値は1e999999999。", "値は2e999999999。")["status"], "FAIL")


if __name__ == "__main__":
    unittest.main()
