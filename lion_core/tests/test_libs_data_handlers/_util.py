import unittest
from lion_core.libs.data_handlers._util import (
    is_homogeneous,
    is_same_dtype,
    is_structure_homogeneous,
    deep_update,
    get_target_container,
)


class TestIsHomogeneousFunction(unittest.TestCase):

    def test_is_homogeneous_with_list(self):
        self.assertTrue(is_homogeneous([1, 2, 3], int))
        self.assertFalse(is_homogeneous([1, "2", 3], int))

    def test_is_homogeneous_with_dict(self):
        self.assertTrue(is_homogeneous({"a": 1, "b": 2}, int))
        self.assertFalse(is_homogeneous({"a": 1, "b": "2"}, int))

    def test_is_homogeneous_with_empty(self):
        self.assertTrue(is_homogeneous([], int))
        self.assertTrue(is_homogeneous({}, int))

    def test_is_homogeneous_with_non_iterable(self):
        self.assertTrue(is_homogeneous(1, int))
        self.assertFalse(is_homogeneous("1", int))


class TestIsSameDtypeFunction(unittest.TestCase):

    def test_is_same_dtype_with_list(self):
        self.assertTrue(is_same_dtype([1, 2, 3], int))
        self.assertFalse(is_same_dtype([1, "2", 3], int))

    def test_is_same_dtype_with_dict(self):
        self.assertTrue(is_same_dtype({"a": 1, "b": 2}, int))
        self.assertFalse(is_same_dtype({"a": 1, "b": "2"}, int))

    def test_is_same_dtype_with_empty(self):
        self.assertTrue(is_same_dtype([]))
        self.assertTrue(is_same_dtype({}))

    def test_is_same_dtype_with_return_dtype(self):
        self.assertEqual(is_same_dtype([1, 2, 3], int, return_dtype=True), (True, int))
        self.assertEqual(
            is_same_dtype([1, "2", 3], int, return_dtype=True), (False, int)
        )


class TestIsStructureHomogeneousFunction(unittest.TestCase):

    def test_is_structure_homogeneous_with_dict(self):
        self.assertTrue(is_structure_homogeneous({"a": {"b": 1}, "c": {"d": 2}}))
        self.assertFalse(is_structure_homogeneous({"a": {"b": 1}, "c": [1, 2]}))

    def test_is_structure_homogeneous_with_list(self):
        self.assertTrue(is_structure_homogeneous([[1], [2]]))
        self.assertFalse(is_structure_homogeneous([{"a": 1}, [1, 2]]))

    def test_is_structure_homogeneous_with_return_type(self):
        self.assertEqual(
            is_structure_homogeneous(
                {"a": {"b": 1}, "c": {"d": 2}}, return_structure_type=True
            ),
            (True, dict),
        )
        self.assertEqual(
            is_structure_homogeneous(
                {"a": {"b": 1}, "c": [1, 2]}, return_structure_type=True
            ),
            (False, None),
        )


class TestDeepUpdateFunction(unittest.TestCase):

    def test_deep_update_basic(self):
        original = {"a": 1, "b": {"x": 2}}
        update = {"b": {"y": 3}, "c": 4}
        result = deep_update(original, update)
        expected = {"a": 1, "b": {"x": 2, "y": 3}, "c": 4}
        self.assertEqual(result, expected)

    def test_deep_update_overwrite(self):
        original = {"a": 1, "b": {"x": 2}}
        update = {"b": {"x": 3}}
        result = deep_update(original, update)
        expected = {"a": 1, "b": {"x": 3}}
        self.assertEqual(result, expected)

    def test_deep_update_with_empty(self):
        original = {}
        update = {"a": 1}
        result = deep_update(original, update)
        expected = {"a": 1}
        self.assertEqual(result, expected)


class TestGetTargetContainerFunction(unittest.TestCase):

    def test_get_target_container_list(self):
        nested = [1, [2, 3], 4]
        indices = [1, 1]
        result = get_target_container(nested, indices)
        expected = 3
        self.assertEqual(result, expected)

    def test_get_target_container_dict(self):
        nested = {"a": {"b": {"c": 1}}}
        indices = ["a", "b"]
        result = get_target_container(nested, indices)
        expected = {"c": 1}
        self.assertEqual(result, expected)

    def test_get_target_container_mixed(self):
        nested = {"a": [1, {"b": 2}]}
        indices = ["a", 1, "b"]
        result = get_target_container(nested, indices)
        expected = 2
        self.assertEqual(result, expected)

    def test_get_target_container_invalid_index(self):
        nested = [1, [2, 3], 4]
        indices = [1, 3]
        with self.assertRaises(IndexError):
            get_target_container(nested, indices)

    def test_get_target_container_invalid_key(self):
        nested = {"a": {"b": {"c": 1}}}
        indices = ["a", "x"]
        with self.assertRaises(KeyError):
            get_target_container(nested, indices)

    def test_get_target_container_invalid_type(self):
        nested = {"a": [1, 2]}
        indices = ["a", "b"]
        with self.assertRaises(IndexError):
            get_target_container(nested, indices)


if __name__ == "__main__":
    unittest.main()
