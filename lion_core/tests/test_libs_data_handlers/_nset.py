import unittest
from lion_core.libs.data_handlers._nset import nset


class TestNSetFunction(unittest.TestCase):

    def test_set_value_in_nested_dict(self):
        data = {"a": {"b": {"c": 3}}}
        nset(data, ["a", "b", "c"], 99)
        self.assertEqual(data, {"a": {"b": {"c": 99}}})

    def test_set_value_in_nested_list(self):
        data = {"a": {"b": [1, 2, 3]}}
        nset(data, ["a", "b", 2], 99)
        self.assertEqual(data, {"a": {"b": [1, 2, 99]}})

    def test_set_value_in_mixed_structure(self):
        data = {"a": [1, {"b": 2}]}
        nset(data, ["a", 1, "b"], 99)
        self.assertEqual(data, {"a": [1, {"b": 99}]})

    def test_set_value_empty_dict(self):
        data = {}
        nset(data, ["a", "b", "c"], 99)
        self.assertEqual(data, {"a": {"b": {"c": 99}}})

    def test_set_value_empty_list(self):
        data = []
        nset(data, [0, "a"], 99)
        self.assertEqual(data, [{"a": 99}])

    def test_set_value_single_level_dict(self):
        data = {"a": 1, "b": 2}
        nset(data, ["b"], 99)
        self.assertEqual(data, {"a": 1, "b": 99})

    def test_set_value_single_level_list(self):
        data = [1, 2, 3]
        nset(data, [1], 99)
        self.assertEqual(data, [1, 99, 3])

    def test_set_value_non_existent_indices(self):
        data = {"a": {"b": 2}}
        nset(data, ["a", "c"], 99)
        self.assertEqual(data, {"a": {"b": 2, "c": 99}})

    def test_set_value_overwrite_existing(self):
        data = {"a": {"b": 2}}
        nset(data, ["a", "b"], 99)
        self.assertEqual(data, {"a": {"b": 99}})

    def test_set_invalid_index_for_list(self):
        data = [1, 2, 3]
        with self.assertRaises(TypeError):
            nset(data, ["a"], 99)

    def test_set_invalid_index_for_dict(self):
        data = {"a": 1}
        with self.assertRaises(TypeError):
            nset(data, [0], 99)

    def test_set_non_container(self):
        data = {"a": {"b": 2}}
        with self.assertRaises(TypeError):
            nset(data, ["a", "b", "c"], 99)


if __name__ == "__main__":
    unittest.main()
