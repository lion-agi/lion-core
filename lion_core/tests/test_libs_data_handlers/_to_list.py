import unittest
from lion_core.libs.data_handlers._to_list import to_list


class TestToListFunction(unittest.TestCase):

    def test_to_list_with_single_element(self):
        self.assertEqual(to_list(1), [1])

    def test_to_list_with_list(self):
        self.assertEqual(to_list([1, 2, 3]), [1, 2, 3])

    def test_to_list_with_flatten(self):
        self.assertEqual(
            to_list([1, [2, 3], [4, [5, 6]]], flatten=True), [1, 2, 3, 4, 5, 6]
        )

    def test_to_list_with_no_flatten(self):
        self.assertEqual(
            to_list([1, [2, 3], [4, [5, 6]]], flatten=False), [1, [2, 3], [4, [5, 6]]]
        )

    def test_to_list_with_dropna(self):
        self.assertEqual(to_list([1, None, 2], dropna=True), [1, 2])

    def test_to_list_with_no_dropna(self):
        self.assertEqual(to_list([1, None, 2], dropna=False), [1, None, 2])

    def test_to_list_with_none_input(self):
        self.assertEqual(to_list(None), [])

    def test_to_list_with_string(self):
        self.assertEqual(to_list("string"), ["string"])

    def test_to_list_with_bytes(self):
        self.assertEqual(to_list(b"bytes"), [b"bytes"])

    def test_to_list_with_bytearray(self):
        self.assertEqual(to_list(bytearray(b"bytearray")), [bytearray(b"bytearray")])

    def test_to_list_with_dict(self):
        self.assertEqual(to_list({"key": "value"}), [{"key": "value"}])


if __name__ == "__main__":
    unittest.main()
