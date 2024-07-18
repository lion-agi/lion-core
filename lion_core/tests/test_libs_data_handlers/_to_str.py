import unittest
from collections import OrderedDict, namedtuple
from pydantic import BaseModel
from lion_core.setting import LionUndefined

# Import the to_str function and strip_lower
from lion_core.libs.data_handlers._to_str import to_str, strip_lower


class CustomModel(BaseModel):
    field: str = "value"


class CustomObject:
    def __str__(self):
        return "CustomObject"


class TestToStr(unittest.TestCase):

    def test_none_input(self):
        self.assertEqual(to_str(None), "")
        self.assertEqual(to_str(LionUndefined()), "")

    def test_primitive_types(self):
        self.assertEqual(to_str(123), "123")
        self.assertEqual(to_str(3.14), "3.14")
        self.assertEqual(to_str(True), "True")

    def test_string_input(self):
        self.assertEqual(to_str("Hello"), "Hello")
        self.assertEqual(to_str("  WORLD  ", strip_lower=True), "world")
        self.assertEqual(to_str("__TEST__", strip_lower=True, chars="_"), "test")

    def test_bytes_and_bytearray(self):
        self.assertEqual(to_str(b"hello"), "hello")
        self.assertEqual(to_str(bytearray(b"world")), "world")

    def test_list_input(self):
        self.assertEqual(to_str([1, 2, 3]), "1, 2, 3")
        self.assertEqual(to_str([1, [2, 3]]), "1, 2, 3")

    def test_tuple_input(self):
        self.assertEqual(to_str((1, 2, 3)), "1, 2, 3")

    def test_set_input(self):
        result = to_str({1, 2, 3})
        self.assertTrue(
            result in ["1, 2, 3", "1, 3, 2", "2, 1, 3", "2, 3, 1", "3, 1, 2", "3, 2, 1"]
        )

    def test_dict_input(self):
        self.assertEqual(to_str({"a": 1, "b": 2}), '{"a": 1, "b": 2}')

    def test_ordereddict_input(self):
        od = OrderedDict([("a", 1), ("b", 2)])
        self.assertEqual(to_str(od), '{"a": 1, "b": 2}')

    def test_nested_structures(self):
        nested = [1, [2, 3], {"a": 4}]
        self.assertEqual(to_str(nested), '1, 2, 3, {"a": 4}')

    def test_pydantic_model(self):
        model = CustomModel(field="test")
        self.assertEqual(to_str(model), '{"field": "test"}')
        self.assertEqual(to_str(model, use_model_dump=False), "field='test'")

    def test_custom_object(self):
        obj = CustomObject()
        self.assertEqual(to_str(obj), "CustomObject")

    def test_strip_lower_function(self):
        self.assertEqual(strip_lower("  HELLO WORLD  "), "hello world")
        self.assertEqual(strip_lower("__TEST__", chars="_"), "test")

    def test_mixed_types_in_sequence(self):
        mixed = [1, "two", 3.0, [4, 5], {"six": 6}]
        expected = '1, two, 3.0, 4, 5, {"six": 6}'
        self.assertEqual(to_str(mixed), expected)

    def test_empty_inputs(self):
        self.assertEqual(to_str([]), "")
        self.assertEqual(to_str({}), "{}")
        self.assertEqual(to_str(set()), "")

    def test_large_input(self):
        large_list = list(range(1000))
        result = to_str(large_list)
        self.assertEqual(len(result.split(", ")), 1000)

    def test_unicode_handling(self):
        self.assertEqual(to_str("こんにちは"), "こんにちは")
        self.assertEqual(to_str("こんにちは".encode()), "こんにちは")

    def test_escape_characters(self):
        text = 'Line 1\nLine 2\t"Quoted"'
        expected = '{"text": "Line 1\\nLine 2\\t\\"Quoted\\""}'
        self.assertEqual(to_str(text), text)
        self.assertEqual(to_str({"text": text}), expected)

    def test_combination_of_options(self):
        data = ["  HELLO  ", {"  WORLD  ": 123}]
        expected = 'hello, {"  world  ": 123}'
        self.assertEqual(to_str(data, strip_lower=True), expected)

    def test_error_handling(self):
        class ErrorObject:
            def __str__(self):
                raise Exception("Str conversion error")

        try:
            a = ErrorObject()
            to_str(a)
        except Exception:
            return True
        return False

    def test_generator(self):
        def gen():
            yield from range(3)

        self.assertEqual(to_str(gen()), "0, 1, 2")

    def test_namedtuple(self):
        Point = namedtuple("Point", ["x", "y"])
        p = Point(1, 2)
        self.assertEqual(to_str(p), "1, 2")


if __name__ == "__main__":
    unittest.main()
