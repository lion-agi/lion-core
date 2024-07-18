# tried works
import unittest
from typing import Any
from collections import deque
from dataclasses import dataclass
from pydantic import BaseModel
from lion_core.libs.data_handlers._to_dict import to_dict, LionUndefined



class MockToDict:
    def to_dict(self):
        return {"mock": "to_dict"}

class MockModelDump:
    def model_dump(self):
        return {"mock": "model_dump"}

class MockJson:
    def json(self):
        return '{"mock": "json"}'

@dataclass
class MockDataclass:
    field: str = "value"

class MockPydanticModel(BaseModel):
    field: str = "value"

class TestToDict(unittest.TestCase):

    def test_dict_input(self):
        input_dict = {"a": 1, "b": 2}
        self.assertEqual(to_dict(input_dict), input_dict)

    def test_list_of_dicts(self):
        input_list = [{"a": 1}, {"b": 2}]
        self.assertEqual(to_dict(input_list), input_list)

    def test_json_string(self):
        json_string = '{"a": 1, "b": 2}'
        self.assertEqual(to_dict(json_string, str_type="json"), {"a": 1, "b": 2})

    def test_xml_string(self):
        xml_string = "<root><a>1</a><b>2</b></root>"
        self.assertEqual(to_dict(xml_string, str_type="xml"), {"root": {"a": "1", "b": "2"}})

    def test_none_input(self):
        self.assertEqual(to_dict(None), {})

    def test_lion_undefined_input(self):
        self.assertEqual(to_dict(LionUndefined()), {})

    def test_empty_input(self):
        self.assertEqual(to_dict({}), {})
        self.assertEqual(to_dict([]), [])
        self.assertEqual(to_dict(""), {})

    def test_sequence_types(self):
        self.assertEqual(to_dict((1, 2, 3)), [1, 2, 3])
        self.assertEqual(to_dict({1, 2, 3}), [1, 2, 3])
        self.assertEqual(to_dict(deque([1, 2, 3])), [1, 2, 3])

    def test_custom_objects(self):
        self.assertEqual(to_dict(MockToDict()), {"mock": "to_dict"})
        self.assertEqual(to_dict(MockModelDump(), use_model_dump=True), {"mock": "model_dump"})
        self.assertEqual(to_dict(MockJson()), {"mock": "json"})

    def test_dataclass_and_pydantic(self):
        self.assertEqual(to_dict(MockDataclass()), {"field": "value"})
        self.assertEqual(to_dict(MockPydanticModel()), {"field": "value"})

    def test_nested_structures(self):
        nested_input = {
            "key1": {"nested_key": "value"},
            "key2": [1, 2, {"nested_list_key": "value"}]
        }
        self.assertEqual(to_dict(nested_input), nested_input)

    def test_use_model_dump_parameter(self):
        mock_obj = MockModelDump()
        self.assertEqual(to_dict(mock_obj, use_model_dump=True), {"mock": "model_dump"})

    def test_custom_parser(self):
        def custom_parser(s: str) -> dict[str, Any]:
            return {"custom": s}
        self.assertEqual(to_dict("test", parser=custom_parser), {"custom": "test"})

    def test_invalid_json_string(self):
        invalid_json = '{"key": "value"'
        self.assertEqual(to_dict(invalid_json, str_type="json"), invalid_json)

    def test_invalid_xml_string(self):
        invalid_xml = "<root><key>value</root>"
        with self.assertRaises(ValueError):
            to_dict(invalid_xml, str_type="xml")

    def test_unsupported_string_type(self):
        with self.assertRaises(ValueError):
            to_dict("test", str_type="yaml")

    def test_unsupported_type(self):
        with self.assertRaises(ValueError):
            to_dict(12345)

    def test_unicode_strings(self):
        unicode_dict = {"ключ": "значение", "キー": "値"}
        self.assertEqual(to_dict(unicode_dict), unicode_dict)

    def test_none_values_in_dict(self):
        dict_with_none = {"key1": None, "key2": "value"}
        self.assertEqual(to_dict(dict_with_none), dict_with_none)

    def test_empty_nested_structures(self):
        empty_nested = {"key1": {}, "key2": [], "key3": set()}
        self.assertEqual(to_dict(empty_nested), {"key1": {}, "key2": [], "key3": set()})

    def test_mixed_type_list(self):
        mixed_list = [1, "string", {"key": "value"}, [1, 2, 3]]
        self.assertEqual(to_dict(mixed_list), mixed_list)

    def test_generator_input(self):
        def gen():
            yield {"key1": "value1"}
            yield {"key2": "value2"}
        self.assertEqual(to_dict(list(gen())), [{"key1": "value1"}, {"key2": "value2"}])

if __name__ == '__main__':
    unittest.main()
