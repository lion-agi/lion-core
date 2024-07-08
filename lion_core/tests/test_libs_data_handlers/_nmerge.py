import unittest
from lion_core.libs.data_handlers._nmerge import nmerge


class TestMergeNestedFunction(unittest.TestCase):

    def test_merge_dicts_without_overwrite(self):
        data = [{"a": 1, "b": 2}, {"b": 3, "c": 4}, {"b": 4, "e": 5}]
        expected = {"a": 1, "b": [2, 3, 4], "c": 4, "e": 5}
        self.assertEqual(nmerge(data), expected)

    def test_merge_dicts_with_overwrite(self):
        data = [{"a": 1, "b": 2}, {"b": 3, "c": 4}]
        expected = {"a": 1, "b": 3, "c": 4}
        self.assertEqual(nmerge(data, overwrite=True), expected)

    def test_merge_dicts_with_sequence_keys(self):
        data = [{"a": 1, "b": 2}, {"b": 3, "c": 4}]
        expected = {"a": 1, "b": 2, "b1": 3, "c": 4}
        self.assertEqual(nmerge(data, dict_sequence=True), expected)

    def test_merge_lists_without_sorting(self):
        data = [[1, 3], [2, 4], [5, 6]]
        expected = [1, 3, 2, 4, 5, 6]
        self.assertEqual(nmerge(data), expected)

    def test_merge_lists_with_sorting(self):
        data = [[3, 1], [6, 2], [5, 4]]
        expected = [1, 2, 3, 4, 5, 6]
        self.assertEqual(nmerge(data, sort_list=True), expected)

    def test_merge_lists_with_custom_sort_key(self):
        data = [["apple", "banana"], ["cherry", "date"]]
        expected = ["date", "apple", "banana", "cherry"]
        self.assertEqual(nmerge(data, sort_list=True, custom_sort=len), expected)

    def test_merge_mixed_structures(self):
        data = [{"a": [1, 2]}, {"a": [3, 4]}]
        expected = {"a": [[1, 2], [3, 4]]}
        self.assertEqual(nmerge(data), expected)

    def test_merge_empty_list(self):
        data = []
        self.assertEqual(nmerge(data), {})

    def test_merge_single_element_list(self):
        data = [{"a": 1}]
        expected = {"a": 1}
        self.assertEqual(nmerge(data), expected)

    def test_merge_with_incompatible_types(self):
        data = [{"a": 1}, [2, 3]]
        with self.assertRaises(TypeError):
            nmerge(data)

    def test_deep_merge_dicts(self):
        data = [{"a": {"b": 1}}, {"a": {"c": 2}}]
        expected = {"a": [{"b": 1}, {"c": 2}]}
        self.assertEqual(nmerge(data), expected)

    def test_invalid_input_structure(self):
        data = "invalid_input"
        with self.assertRaises(TypeError):
            nmerge(data)


if __name__ == "__main__":
    unittest.main()
