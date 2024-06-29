import unittest
from lion_core.libs.data_handlers._npop import npop


class TestNPopFunction(unittest.TestCase):

    def test_npop_dict(self):
        data = {'a': {'b': {'c': 3}}}
        self.assertEqual(npop(data, ['a', 'b', 'c']), 3)
        self.assertEqual(data, {'a': {'b': {}}})

    def test_npop_list(self):
        data = {'a': {'b': [1, 2, 3]}}
        self.assertEqual(npop(data, ['a', 'b', 2]), 3)
        self.assertEqual(data, {'a': {'b': [1, 2]}})

    def test_npop_mixed(self):
        data = {'a': [1, {'b': 2}]}
        self.assertEqual(npop(data, ['a', 1, 'b']), 2)
        self.assertEqual(data, {'a': [1, {}]})

    def test_npop_empty_dict(self):
        data = {}
        with self.assertRaises(KeyError):
            npop(data, ['a'])

    def test_npop_empty_list(self):
        data = []
        with self.assertRaises(KeyError):
            npop(data, [0])

    def test_npop_single_level(self):
        data = {'a': 1, 'b': 2}
        self.assertEqual(npop(data, ['b']), 2)
        self.assertEqual(data, {'a': 1})

    def test_npop_non_existent_default(self):
        data = {'a': {'b': 2}}
        self.assertEqual(npop(data, ['a', 'c'], default=10), 10)
        self.assertEqual(data, {'a': {'b': 2}})

    def test_npop_non_existent_no_default(self):
        data = {'a': {'b': 2}}
        with self.assertRaises(KeyError):
            npop(data, ['a', 'c'])

    def test_npop_invalid_index_for_list(self):
        data = [1, 2, 3]
        with self.assertRaises(KeyError):
            npop(data, ['a'])

    def test_npop_invalid_index_for_dict(self):
        data = {'a': 1}
        with self.assertRaises(KeyError):
            npop(data, [0])


if __name__ == '__main__':
    unittest.main()
