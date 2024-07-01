import unittest
from lion_core.libs.data_handlers._unflatten import unflatten


class TestUnflattenFunction(unittest.TestCase):

    def test_unflatten_dict(self):
        flat_dict = {
            "a|b|c": 1,
            "a|b|d": 2,
            "a|e": 3,
            "f": 4
        }
        result = unflatten(flat_dict, sep="|")
        expected = {
            "a": {
                "b": {
                    "c": 1,
                    "d": 2
                },
                "e": 3
            },
            "f": 4
        }
        self.assertEqual(result, expected)

    def test_unflatten_dict_with_custom_separator(self):
        flat_dict = {
            "a/b/c": 1,
            "a/b/d": 2,
            "a/e": 3,
            "f": 4
        }
        result = unflatten(flat_dict, sep="/")
        expected = {
            "a": {
                "b": {
                    "c": 1,
                    "d": 2
                },
                "e": 3
            },
            "f": 4
        }
        self.assertEqual(result, expected)

    def test_unflatten_dict_with_inplace(self):
        flat_dict = {
            "a|b|c": 1,
            "a|b|d": 2,
            "a|e": 3,
            "f": 4
        }
        result = unflatten(flat_dict, sep="|", inplace=True)
        expected = {
            "a": {
                "b": {
                    "c": 1,
                    "d": 2
                },
                "e": 3
            },
            "f": 4
        }
        self.assertEqual(result, expected)
        self.assertEqual(flat_dict, expected)

    def test_unflatten_list(self):
        flat_dict = {
            "0": "a",
            "1|b|c": 1,
            "1|b|d": 2,
            "1|e": 3,
            "2": "f"
        }
        result = unflatten(flat_dict, sep="|")
        expected = [
            "a",
            {
                "b": {
                    "c": 1,
                    "d": 2
                },
                "e": 3
            },
            "f"
        ]
        self.assertEqual(result, expected)

    def test_unflatten_empty_dict(self):
        flat_dict = {}
        result = unflatten(flat_dict, sep="|")
        expected = {}
        self.assertEqual(result, expected)

    def test_unflatten_dict_with_mixed_types(self):
        flat_dict = {
            "a|b|0": 1,
            "a|b|1": 2,
            "a|c|d": 3
        }
        result = unflatten(flat_dict, sep="|")
        expected = {
            "a": {
                "b": [1, 2],
                "c": {
                    "d": 3
                }
            }
        }
        self.assertEqual(result, expected)


if __name__ == '__main__':
    unittest.main()
