import unittest
import json
from lion_core.libs.data_handlers._to_str import to_str


class TestToStrFunction(unittest.TestCase):

    def test_to_str_with_dict(self):
        input_data = {"key": "value"}
        result = to_str(input_data)
        expected = json.dumps(input_data)
        self.assertEqual(result, expected)

    def test_to_str_with_list(self):
        input_data = ["a", "b", "c"]
        result = to_str(input_data)
        expected = "a, b, c"
        self.assertEqual(result, expected)

    def test_to_str_with_nested_list(self):
        input_data = ["a", ["b", "c"], "d"]
        result = to_str(input_data)
        expected = "a, b, c, d"
        self.assertEqual(result, expected)

    def test_to_str_with_string(self):
        input_data = "   Example String   "
        result = to_str(input_data, strip_lower=True)
        expected = "example string"
        self.assertEqual(result, expected)

    def test_to_str_with_int(self):
        input_data = 42
        result = to_str(input_data)
        expected = "42"
        self.assertEqual(result, expected)

    def test_to_str_with_float(self):
        input_data = 3.14
        result = to_str(input_data)
        expected = "3.14"
        self.assertEqual(result, expected)

    def test_to_str_with_none(self):
        input_data = None
        result = to_str(input_data)
        expected = "None"
        self.assertEqual(result, expected)


if __name__ == "__main__":
    unittest.main()
