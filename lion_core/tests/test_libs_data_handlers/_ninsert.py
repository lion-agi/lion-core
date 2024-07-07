import unittest

from lion_core.libs.data_handlers._ninsert import ninsert


class TestNInsertFunction(unittest.TestCase):

    def test_insert_into_nested_dict(self):
        data = {"a": {"b": [1, 2]}}
        ninsert(data, ["a", "b", 2], 3)
        self.assertEqual(data, {"a": {"b": [1, 2, 3]}})

    def test_insert_into_nested_list(self):
        data = [1, [2, 3]]
        ninsert(data, [1, 2], 4)
        self.assertEqual(data, [1, [2, 3, 4]])

    def test_insert_into_mixed_structure(self):
        data = {"a": [1, {"b": 2}]}
        ninsert(data, ["a", 1, "c"], 3)
        self.assertEqual(data, {"a": [1, {"b": 2, "c": 3}]})

    def test_empty_indices(self):
        data = {"a": 1}
        with self.assertRaises(ValueError):
            ninsert(data, [], 2)

    def test_create_intermediate_structures(self):
        data = {}
        ninsert(data, ["a", "b", "c"], 1)
        self.assertEqual(data, {"a": {"b": {"c": 1}}})

    def test_overwrite_existing_value(self):
        data = {"a": {"b": 2}}
        ninsert(data, ["a", "b"], 3)
        self.assertEqual(data, {"a": {"b": 3}})

    def test_invalid_index_for_list(self):
        data = [1, 2, 3]
        with self.assertRaises(TypeError):
            ninsert(data, ["a"], 4)

    def test_invalid_index_for_dict(self):
        data = {"a": 1}
        with self.assertRaises(TypeError):
            ninsert(data, [0], 2)

    def test_insert_into_non_container(self):
        data = {"a": {"b": 2}}
        with self.assertRaises(TypeError):
            ninsert(data, ["a", "b", "c"], 3)

    def test_handle_list_insert_function(self):
        data = {"a": {"b": [1, 2]}}
        ninsert(data, ["a", "b", 5], 3)
        self.assertEqual(data, {"a": {"b": [1, 2, None, None, None, 3]}})


if __name__ == "__main__":
    unittest.main()
