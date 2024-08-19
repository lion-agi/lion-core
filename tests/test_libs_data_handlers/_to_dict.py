import pytest
from typing import Any
from collections import deque, OrderedDict, namedtuple
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


@pytest.fixture
def complex_nested_structure():
    return {
        "int": 1,
        "float": 2.0,
        "str": "three",
        "list": [4, 5, 6],
        "dict": {"seven": 7, "eight": 8},
        "tuple": (9, 10),
        "set": {11, 12},
        "none": None,
        "bool": True,
        "dataclass": MockDataclass(),
        "pydantic": MockPydanticModel(),
        "custom": MockToDict(),
    }


def test_dict_input():
    input_dict = {"a": 1, "b": 2}
    assert to_dict(input_dict) == input_dict


def test_list_of_dicts():
    input_list = [{"a": 1}, {"b": 2}]
    assert to_dict(input_list) == input_list


@pytest.mark.parametrize(
    "json_string, expected",
    [
        ('{"a": 1, "b": 2}', {"a": 1, "b": 2}),
        ('{"x": [1, 2, 3], "y": {"z": true}}', {"x": [1, 2, 3], "y": {"z": True}}),
    ],
)
def test_json_string(json_string, expected):
    assert to_dict(json_string, str_type="json") == expected


def test_xml_string():
    xml_string = "<root><a>1</a><b>2</b></root>"
    assert to_dict(xml_string, str_type="xml") == {"root": {"a": "1", "b": "2"}}


@pytest.mark.parametrize(
    "input_value, expected",
    [
        (None, {}),
        (LionUndefined(), {}),
    ],
)
def test_none_and_undefined_input(input_value, expected):
    assert to_dict(input_value) == expected


@pytest.mark.parametrize(
    "input_value, expected",
    [
        ({}, {}),
        ([], []),
        ("", {}),
    ],
)
def test_empty_input(input_value, expected):
    assert to_dict(input_value) == expected


@pytest.mark.parametrize(
    "input_value, expected",
    [
        ((1, 2, 3), [1, 2, 3]),
        ({1, 2, 3}, [1, 2, 3]),
        (deque([1, 2, 3]), [1, 2, 3]),
    ],
)
def test_sequence_types(input_value, expected):
    assert to_dict(input_value) == expected


@pytest.mark.parametrize(
    "input_value, expected",
    [
        (MockToDict(), {"mock": "to_dict"}),
        (MockJson(), {"mock": "json"}),
    ],
)
def test_custom_objects(input_value, expected):
    assert to_dict(input_value) == expected


def test_model_dump():
    assert to_dict(MockModelDump(), use_model_dump=True) == {"mock": "model_dump"}


@pytest.mark.parametrize(
    "input_value, expected",
    [
        (MockDataclass(), {"field": "value"}),
        (MockPydanticModel(), {"field": "value"}),
    ],
)
def test_dataclass_and_pydantic(input_value, expected):
    assert to_dict(input_value) == expected


def test_nested_structures(complex_nested_structure):
    result = to_dict(complex_nested_structure)
    assert result["int"] == 1
    assert result["float"] == 2.0
    assert result["str"] == "three"
    assert result["list"] == [4, 5, 6]
    assert result["dict"] == {"seven": 7, "eight": 8}
    assert result["tuple"] == [9, 10]
    assert set(result["set"]) == {11, 12}
    assert result["none"] is None
    assert result["bool"] is True
    assert result["dataclass"] == {"field": "value"}
    assert result["pydantic"] == {"field": "value"}
    assert result["custom"] == {"mock": "to_dict"}


def test_use_model_dump_parameter():
    mock_obj = MockModelDump()
    assert to_dict(mock_obj, use_model_dump=True) == {"mock": "model_dump"}


def test_custom_parser():
    def custom_parser(s: str) -> dict[str, Any]:
        return {"custom": s}

    assert to_dict("test", parser=custom_parser) == {"custom": "test"}


def test_invalid_json_string():
    invalid_json = '{"key": "value"'
    assert to_dict(invalid_json, str_type="json") == invalid_json


def test_invalid_xml_string():
    invalid_xml = "<root><key>value</root>"
    with pytest.raises(ValueError):
        to_dict(invalid_xml, str_type="xml")


def test_unsupported_string_type():
    with pytest.raises(ValueError):
        to_dict("test", str_type="yaml")


def test_unsupported_type():
    with pytest.raises(ValueError):
        to_dict(12345)


def test_unicode_strings():
    unicode_dict = {"ключ": "значение", "キー": "値"}
    assert to_dict(unicode_dict) == unicode_dict


def test_none_values_in_dict():
    dict_with_none = {"key1": None, "key2": "value"}
    assert to_dict(dict_with_none) == dict_with_none


def test_empty_nested_structures():
    empty_nested = {"key1": {}, "key2": [], "key3": set()}
    assert to_dict(empty_nested) == {"key1": {}, "key2": [], "key3": set()}


def test_mixed_type_list():
    mixed_list = [1, "string", {"key": "value"}, [1, 2, 3]]
    assert to_dict(mixed_list) == mixed_list


def test_generator_input():
    def gen():
        yield {"key1": "value1"}
        yield {"key2": "value2"}

    assert to_dict(gen()) == [{"key1": "value1"}, {"key2": "value2"}]


def test_ordered_dict():
    od = OrderedDict([("a", 1), ("b", 2), ("c", 3)])
    assert to_dict(od) == {"a": 1, "b": 2, "c": 3}


def test_named_tuple():
    Point = namedtuple("Point", ["x", "y"])
    p = Point(1, 2)
    assert to_dict(p) == {"x": 1, "y": 2}


def test_custom_class_with_dict():
    class CustomClass:
        def __init__(self):
            self.a = 1
            self.b = 2

    assert to_dict(CustomClass()) == {"a": 1, "b": 2}


def test_bytes_input():
    assert to_dict(b"hello") == b"hello"


def test_bytearray_input():
    assert to_dict(bytearray(b"hello")) == bytearray(b"hello")


def test_frozenset_input():
    assert set(to_dict(frozenset([1, 2, 3]))) == {1, 2, 3}


def test_complex_number():
    assert to_dict(1 + 2j) == (1 + 2j)


def test_recursive_structure():
    recursive = {"a": 1}
    recursive["b"] = recursive
    with pytest.raises(RecursionError):
        to_dict(recursive)


def test_large_nested_structure(benchmark):
    large_structure = {"level1": {}}
    current = large_structure["level1"]
    for i in range(2, 1000):
        current[f"level{i}"] = {}
        current = current[f"level{i}"]
    current["value"] = "deep"

    result = benchmark(to_dict, large_structure)
    assert result["level1"]["level2"]["level3"] is not None
    assert result["level1"]["level2"]["level3"]["level4"] is not None


import json


def test_custom_json_encoder():
    class CustomEncoder(json.JSONEncoder):
        def default(self, obj):
            if isinstance(obj, complex):
                return [obj.real, obj.imag]
            return json.JSONEncoder.default(self, obj)

    data = {"complex": 1 + 2j}
    result = to_dict(data, cls=CustomEncoder)
    assert result == {"complex": [1.0, 2.0]}


@pytest.mark.parametrize(
    "input_value, expected",
    [
        (True, True),
        (False, False),
        (None, None),
    ],
)
def test_boolean_and_none_values(input_value, expected):
    assert to_dict(input_value) == expected


def test_dataclass_with_default_factory():
    from dataclasses import dataclass, field

    @dataclass
    class WithFactory:
        items: list = field(default_factory=list)

    assert to_dict(WithFactory()) == {"items": []}


def test_pydantic_model_with_alias():
    from pydantic import BaseModel, Field

    class ModelWithAlias(BaseModel):
        long_name: str = Field(alias="short")

    model = ModelWithAlias(short="value")
    assert to_dict(model) == {"long_name": "value"}


def test_enum_conversion():
    from enum import Enum

    class Color(Enum):
        RED = 1
        GREEN = 2

    assert to_dict(Color.RED) == 1


def test_date_and_datetime():
    from datetime import date, datetime

    assert to_dict(date(2023, 1, 1)) == "2023-01-01"
    assert to_dict(datetime(2023, 1, 1, 12, 0)) == "2023-01-01T12:00:00"


def test_uuid_conversion():
    import uuid

    u = uuid.uuid4()
    assert to_dict(u) == str(u)


# File: tests/test_to_dict.py
