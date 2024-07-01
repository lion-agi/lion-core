import unittest

from lion_core.libs.data_handlers._nget import nget


class TestGetNestedFunction(unittest.TestCase):

    def test_nget_dict(self):
        data = {'a': {'b': {'c': 3}}}
        indices = ['a', 'b', 'c']
        self.assertEqual(nget(data, indices), 3)

    def test_nget_list(self):
        data = [1, [2, [3, 4]]]
        indices = [1, 1, 0]
        self.assertEqual(nget(data, indices), 3)

    def test_nget_mixed(self):
        data = {'a': [1, {'b': 2}]}
        indices = ['a', 1, 'b']
        self.assertEqual(nget(data, indices), 2)

    def test_nget_empty_dict(self):
        data = {}
        indices = ['a']
        with self.assertRaises(LookupError):
            nget(data, indices)

    def test_nget_empty_list(self):
        data = []
        indices = [0]
        with self.assertRaises(LookupError):
            nget(data, indices)

    def test_nget_single_level(self):
        data = {'a': 1, 'b': 2}
        indices = ['b']
        self.assertEqual(nget(data, indices), 2)

    def test_nget_non_existent_default(self):
        data = {'a': {'b': 2}}
        indices = ['a', 'c']
        self.assertEqual(nget(data, indices, default=10), 10)

    def test_nget_non_existent_no_default(self):
        data = {'a': {'b': 2}}
        indices = ['a', 'c']
        with self.assertRaises(LookupError):
            nget(data, indices)

    def test_nget_invalid_index_for_list(self):
        data = [1, 2, 3]
        indices = ['a']
        with self.assertRaises(LookupError):
            nget(data, indices)

    def test_nget_invalid_index_for_dict(self):
        data = {'a': 1}
        indices = [0]
        with self.assertRaises(LookupError):
            nget(data, indices)

    def test_nget_type_error(self):
        data = {'a': [1, 2, 3]}
        indices = ['a', 'b']
        with self.assertRaises(LookupError):
            nget(data, indices)


if __name__ == '__main__':
    unittest.main()
