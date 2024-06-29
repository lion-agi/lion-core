import unittest
from lion_core.libs.data_handlers._to_num import to_num


class TestToNumFunction(unittest.TestCase):

    def test_to_num_integer(self):
        self.assertEqual(to_num("42", num_type=int), 42)

    def test_to_num_float(self):
        self.assertEqual(to_num("3.14", num_type=float), 3.14)

    def test_to_num_fraction(self):
        self.assertAlmostEqual(to_num("2/3", num_type=float), 2/3)

    def test_to_num_scientific_notation(self):
        self.assertEqual(to_num("1e3", num_type=float), 1e3)

    def test_to_num_complex(self):
        self.assertEqual(to_num("1+2j", num_type=complex), 1+2j)

    def test_to_num_precision(self):
        self.assertEqual(to_num("3.14159", num_type=float, precision=2), 3.14)

    def test_to_num_upper_bound(self):
        with self.assertRaises(ValueError):
            to_num("100", num_type=int, upper_bound=50)

    def test_to_num_lower_bound(self):
        with self.assertRaises(ValueError):
            to_num("10", num_type=int, lower_bound=20)

    def test_to_num_multiple_numbers(self):
        self.assertEqual(to_num("1 and 2 and 3", num_count=3), [1.0, 2.0, 3.0])

    def test_to_num_invalid_input(self):
        with self.assertRaises(ValueError):
            to_num("not a number")

    def test_to_num_invalid_num_type(self):
        with self.assertRaises(ValueError):
            to_num("42", num_type="invalid")

    def test_to_num_hexadecimal(self):
        with self.assertRaises(ValueError):
            to_num("0x1A")

    def test_to_num_binary(self):
        with self.assertRaises(ValueError):
            to_num("0b1010")


if __name__ == '__main__':
    unittest.main()
