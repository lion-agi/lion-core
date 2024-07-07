import unittest

from lion_core.libs.data_handlers._nfilter import nfilter


class TestFilterNestedFunction(unittest.TestCase):

    def test_filter_nested_dict(self):
        data = {"a": 1, "b": {"c": 2, "d": 3}, "e": [4, 5, 6]}
        condition = lambda x: isinstance(x, int) and x % 2 == 0
        expected = {"b": {"c": 2}, "e": [4, 6]}
        self.assertEqual(nfilter(data, condition), expected)

    def test_filter_nested_list(self):
        data = [1, 2, [3, 4], {"a": 5, "b": 6}]
        condition = lambda x: isinstance(x, int) and x % 2 == 0
        expected = [2, [4], {"b": 6}]
        self.assertEqual(nfilter(data, condition), expected)

    def test_filter_mixed_types(self):
        data = {"a": [1, {"b": 2, "c": [3, 4]}], "d": 5}
        condition = lambda x: isinstance(x, int) and x % 2 == 0
        expected = {"a": [{"b": 2, "c": [4]}]}
        self.assertEqual(nfilter(data, condition), expected)

    def test_empty_dict(self):
        self.assertEqual(nfilter({}, lambda x: True), {})

    def test_empty_list(self):
        self.assertEqual(nfilter([], lambda x: True), [])

    def test_single_level_dict(self):
        data = {"a": 1, "b": 2, "c": 3}
        condition = lambda x: x > 1
        expected = {"b": 2, "c": 3}
        self.assertEqual(nfilter(data, condition), expected)

    def test_single_level_list(self):
        data = [1, 2, 3, 4, 5]
        condition = lambda x: x % 2 == 0
        expected = [2, 4]
        self.assertEqual(nfilter(data, condition), expected)

    def test_mixed_types_dict(self):
        data = {"a": 1, "b": "string", "c": [2, 3], "d": {"e": 4}}
        condition = lambda x: isinstance(x, int)
        expected = {"a": 1, "c": [2, 3], "d": {"e": 4}}
        self.assertEqual(nfilter(data, condition), expected)

    def test_mixed_types_list(self):
        data = [1, "string", [2, 3], {"a": 4}]
        condition = lambda x: isinstance(x, int)
        expected = [1, [2, 3], {"a": 4}]
        self.assertEqual(nfilter(data, condition), expected)

    def test_invalid_input(self):
        with self.assertRaises(TypeError):
            nfilter(42, lambda x: True)


if __name__ == "__main__":
    unittest.main()
