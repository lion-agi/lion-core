import unittest

from lion_core.libs.data_handlers._flatten import flatten, get_flattened_keys


class TestFlattenFunction(unittest.TestCase):

    def test_flatten_nested_dict(self):
        data = {'a': 1, 'b': {'c': 2, 'd': {'e': 3}}}
        expected = {'a': 1, 'b|c': 2, 'b|d|e': 3}
        self.assertEqual(flatten(data), expected)

    def test_flatten_nested_list(self):
        data = {'a': 1, 'b': [1, 2, {'c': 3}]}
        expected = {'a': 1, 'b|0': 1, 'b|1': 2, 'b|2|c': 3}
        self.assertEqual(flatten(data), expected)

    def test_flatten_mixed_types(self):
        data = {'a': [1, {'b': 2}], 'c': {'d': [3, {'e': 4}]}}
        expected = {'a|0': 1, 'a|1|b': 2, 'c|d|0': 3, 'c|d|1|e': 4}
        self.assertEqual(flatten(data), expected)

    def test_flatten_empty_dict(self):
        self.assertEqual(flatten({}), {})

    def test_flatten_empty_list(self):
        self.assertEqual(flatten([]), {})

    def test_flatten_single_level(self):
        data = {'a': 1, 'b': 2, 'c': 3}
        self.assertEqual(flatten(data), data)

    def test_flatten_with_max_depth(self):
        data = {'a': 1, 'b': {'c': 2, 'd': {'e': 3}}}
        expected = {'a': 1, 'b|c': 2, 'b|d': {'e': 3}}
        self.assertEqual(flatten(data, max_depth=2), expected)

    def test_flatten_in_place(self):
        data = {'a': 1, 'b': {'c': 2, 'd': {'e': 3}}}
        flatten(data, inplace=True)
        expected = {'a': 1, 'b|c': 2, 'b|d|e': 3}
        self.assertEqual(data, expected)

    def test_flatten_dicts_only(self):
        data = {'a': 1, 'b': {'c': 2, 'd': [3, {'e': 4}]}}
        expected = {'a': 1, 'b|c': 2, 'b|d': [3, {'e': 4}]}
        self.assertEqual(flatten(data, dict_only=True), expected)

    def test_flatten_with_custom_separator(self):
        data = {'a': 1, 'b': {'c': 2, 'd': {'e': 3}}}
        expected = {'a': 1, 'b/c': 2, 'b/d/e': 3}
        self.assertEqual(flatten(data, sep='/'), expected)

    def test_get_flattened_keys(self):
        data = {'a': 1, 'b': {'c': 2, 'd': {'e': 3}}}
        expected = ['a', 'b|c', 'b|d|e']
        self.assertEqual(get_flattened_keys(data), expected)

    def test_flatten_invalid_in_place(self):
        data = [1, 2, 3]
        with self.assertRaises(ValueError):
            flatten(data, inplace=True)

    def test_flatten_none_data(self):
        data = None
        expected = {"": None}
        self.assertEqual(flatten(data), expected)


if __name__ == '__main__':
    unittest.main()
