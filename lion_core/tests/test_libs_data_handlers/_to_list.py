import unittest
from collections import deque, OrderedDict, namedtuple
from pydantic import BaseModel
from lion_core.setting import LionUndefined
from lion_core.libs.data_handlers._to_list import to_list

class CustomIterable:
    def __iter__(self):
        return iter([1, 2, 3])

class CustomMapping:
    def __getitem__(self, key):
        return {1: 'a', 2: 'b', 3: 'c'}[key]
    def keys(self):
        return [1, 2, 3]

class TestModel(BaseModel):
    field: str = "value"

class TestToList(unittest.TestCase):

    def test_none_input(self):
        self.assertEqual(to_list(None), [])
        self.assertEqual(to_list(LionUndefined()), [])

    def test_primitive_types(self):
        self.assertEqual(to_list(1), [1])
        self.assertEqual(to_list(1.5), [1.5])
        self.assertEqual(to_list(True), [True])

    def test_string_types(self):
        self.assertEqual(to_list("string"), ["string"])
        self.assertEqual(to_list(b"bytes"), [b"bytes"])
        self.assertEqual(to_list(bytearray(b"bytearray")), [bytearray(b"bytearray")])

    def test_list_input(self):
        self.assertEqual(to_list([1, 2, 3]), [1, 2, 3])
        self.assertEqual(to_list([1, [2, 3]]), [1, [2, 3]])
        self.assertEqual(to_list([1, [2, 3]], flatten=True), [1, 2, 3])

    def test_tuple_input(self):
        self.assertEqual(to_list((1, 2, 3)), [1, 2, 3])
        self.assertEqual(to_list((1, (2, 3))), [1, (2, 3)])
        self.assertEqual(to_list((1, (2, 3)), flatten=True), [1, 2, 3])

    def test_set_input(self):
        self.assertEqual(set(to_list({1, 2, 3})), {1, 2, 3})

    def test_dict_input(self):
        self.assertEqual(to_list({"a": 1, "b": 2}), [{"a": 1, "b": 2}])

    def test_ordereddict_input(self):
        od = OrderedDict([('a', 1), ('b', 2)])
        self.assertEqual(to_list(od), [od])

    def test_custom_mapping(self):
        cm = CustomMapping()
        self.assertEqual(to_list(cm), [cm])

    def test_generator_input(self):
        def gen():
            yield from range(3)
        self.assertEqual(to_list(gen()), [0, 1, 2])

    def test_custom_iterable(self):
        ci = CustomIterable()
        self.assertEqual(to_list(ci), [1, 2, 3])

    def test_deque_input(self):
        d = deque([1, 2, 3])
        self.assertEqual(to_list(d), [1, 2, 3])

    def test_namedtuple_input(self):
        Point = namedtuple('Point', ['x', 'y'])
        p = Point(1, 2)
        self.assertEqual(to_list(p), [1, 2])

    def test_pydantic_model(self):
        model = TestModel()
        self.assertEqual(to_list(model), [model])

    def test_nested_structures(self):
        nested = [1, [2, [3, [4]]]]
        self.assertEqual(to_list(nested), nested)
        self.assertEqual(to_list(nested, flatten=True), [1, 2, 3, 4])

    def test_mixed_types(self):
        mixed = [1, "two", [3, [4, "five"]]]
        self.assertEqual(to_list(mixed), mixed)
        self.assertEqual(to_list(mixed, flatten=True), [1, "two", 3, 4, "five"])

    def test_dropna(self):
        with_none = [1, None, 2, [3, None, 4]]
        self.assertEqual(to_list(with_none, dropna=True), [1, 2, [3, 4]])
        self.assertEqual(to_list(with_none, flatten=True, dropna=True), [1, 2, 3, 4])

    def test_empty_inputs(self):
        self.assertEqual(to_list([]), [])
        self.assertEqual(to_list({}), [{}])
        self.assertEqual(to_list(set()), [])

    def test_large_input(self):
        large_list = list(range(10000))
        self.assertEqual(to_list(large_list), large_list)

    def test_flatten_with_strings(self):
        input_with_strings = [1, "nested", [2, ["deep", "list"]]]
        self.assertEqual(to_list(input_with_strings, flatten=True), [1, "nested", 2, "deep", "list"])

    def test_flatten_with_tuple(self):
        input_with_tuple = [1, (2, 3), [4, (5, 6)]]
        self.assertEqual(to_list(input_with_tuple, flatten=True), [1, 2, 3, 4, 5, 6])

    def test_flatten_with_set(self):
        input_with_set = [1, {2, 3}, [4, {5, 6}]]
        flattened = to_list(input_with_set, flatten=True)
        self.assertEqual(len(flattened), 6)
        self.assertIn(1, flattened)
        self.assertIn(2, flattened)
        self.assertIn(3, flattened)
        self.assertIn(4, flattened)
        self.assertIn(5, flattened)
        self.assertIn(6, flattened)

    def test_flatten_with_dict(self):
        input_with_dict = [1, {"a": 2}, [3, {"b": 4}]]
        self.assertEqual(to_list(input_with_dict, flatten=True), [1, {"a": 2}, 3, {"b": 4}])

    def test_generator_with_none(self):
        def gen_with_none():
            yield 1
            yield None
            yield 2
        self.assertEqual(to_list(gen_with_none(), dropna=True), [1, 2])

    def test_deeply_nested_structure(self):
        deeply_nested = [1, [2, [3, [4, [5, [6]]]]]]
        self.assertEqual(to_list(deeply_nested, flatten=True), [1, 2, 3, 4, 5, 6])

    def test_input_with_all_none(self):
        self.assertEqual(to_list([None, None, None], dropna=True), [])

    def test_custom_objects(self):
        class CustomObj:
            pass
        obj = CustomObj()
        self.assertEqual(to_list(obj), [obj])

    def test_flatten_with_empty_nested_structures(self):
        input_with_empty = [1, [], [2, []], [[], 3]]
        self.assertEqual(to_list(input_with_empty, flatten=True), [1, 2, 3])

    def test_flatten_and_dropna_combination(self):
        complex_input = [1, None, [2, None, [3, None, 4]]]
        self.assertEqual(to_list(complex_input, flatten=True, dropna=True), [1, 2, 3, 4])

    def test_input_types_preservation(self):
        mixed_types = [1, "two", 3.0, True, b"four"]
        self.assertEqual(to_list(mixed_types), mixed_types)

    def test_very_large_nested_structure(self):
        large_nested = list(range(1000)) + [list(range(1000, 2000))]
        flattened = to_list(large_nested, flatten=True)
        self.assertEqual(len(flattened), 2000)
        self.assertEqual(flattened[-1], 1999)

if __name__ == '__main__':
    unittest.main()