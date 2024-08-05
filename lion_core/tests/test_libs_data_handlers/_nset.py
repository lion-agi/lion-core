import pytest
from lion_core.libs.data_handlers._nset import nset


@pytest.mark.parametrize(
    "data, indices, value, expected",
    [
        ({"a": {"b": {"c": 3}}}, ["a", "b", "c"], 99, {"a": {"b": {"c": 99}}}),
        ({"a": {"b": [1, 2, 3]}}, ["a", "b", 2], 99, {"a": {"b": [1, 2, 99]}}),
        ({"a": [1, {"b": 2}]}, ["a", 1, "b"], 99, {"a": [1, {"b": 99}]}),
        ({}, ["a", "b", "c"], 99, {"a": {"b": {"c": 99}}}),
        ([], [0, "a"], 99, [{"a": 99}]),
        ({"a": 1, "b": 2}, ["b"], 99, {"a": 1, "b": 99}),
        ([1, 2, 3], [1], 99, [1, 99, 3]),
        ({"a": {"b": 2}}, ["a", "c"], 99, {"a": {"b": 2, "c": 99}}),
    ],
)
def test_nset_various_scenarios(data, indices, value, expected):
    nset(data, indices, value)
    assert data == expected


def test_nset_empty_indices():
    data = {"a": 1}
    with pytest.raises(ValueError, match="Indices list cannot be empty"):
        nset(data, [], 2)


@pytest.mark.parametrize(
    "data, indices, value",
    [
        ([1, 2, 3], ["a"], 4),
        ({"a": 1}, [0], 2),
        ({"a": {"b": 2}}, ["a", "b", "c"], 3),
    ],
)
def test_nset_type_errors(data, indices, value):
    with pytest.raises(TypeError):
        nset(data, indices, value)


def test_nset_nested_creation():
    data = {}
    nset(data, ["a", 0, "b", 1, "c"], 42)
    assert data == {"a": [{"b": [None, {"c": 42}]}]}


def test_nset_overwrite_existing():
    data = {"a": {"b": {"c": 1}}}
    nset(data, ["a", "b", "c"], 2)
    assert data == {"a": {"b": {"c": 2}}}


def test_nset_extend_list():
    data = {"a": [1, 2]}
    nset(data, ["a", 5], 3)
    assert data == {"a": [1, 2, None, None, None, 3]}


def test_nset_with_tuple():
    data = {"a": (1, 2)}
    with pytest.raises(TypeError):
        nset(data, ["a", 2], 3)


def test_nset_with_set():
    data = {"a": {1, 2}}
    with pytest.raises(TypeError):
        nset(data, ["a", 3], 3)


def test_nset_with_none():
    data = {"a": None}
    nset(data, ["a", "b"], 1)
    assert data == {"a": {"b": 1}}


def test_nset_with_custom_object():
    class CustomObj:
        def __init__(self):
            self.data = {}

        def __setitem__(self, key, value):
            self.data[key] = value

    obj = CustomObj()
    nset(obj, ["data", "key"], "value")
    assert obj.data == {"key": "value"}


def test_nset_with_property():
    class PropObj:
        def __init__(self):
            self._data = {}

        @property
        def data(self):
            return self._data

    obj = PropObj()
    nset(obj, ["data", "key"], "value")
    assert obj._data == {"key": "value"}


def test_nset_with_large_nested_structure():
    data = {}
    for i in range(1000):
        nset(data, ["level" + str(i)], i)
    assert data["level999"] == 999


def test_nset_performance_with_large_list(benchmark):
    def insert_many():
        data = []
        for i in range(10**5):
            nset(data, [i], i)

    benchmark(insert_many)


@pytest.mark.parametrize(
    "data, indices, value, expected",
    [
        ({"a": 1}, ["b", "c"], 2, {"a": 1, "b": {"c": 2}}),
        ([1, 2], [2, "a"], 3, [1, 2, {"a": 3}]),
        ({}, ["a", 0, "b"], 1, {"a": [{"b": 1}]}),
    ],
)
def test_nset_create_intermediate_structures(data, indices, value, expected):
    nset(data, indices, value)
    assert data == expected


def test_nset_with_negative_list_index():
    data = [1, 2, 3]
    with pytest.raises(ValueError, match="list index cannot be negative"):
        nset(data, [-1], 4)


def test_nset_with_string_key_for_list():
    data = [1, 2, 3]
    with pytest.raises(TypeError, match="Cannot use non-integer index on a list"):
        nset(data, ["key"], 4)


def test_nset_with_int_key_for_dict():
    data = {}
    nset(data, [1], "value")
    assert data == {1: "value"}


def test_nset_with_existing_none_value():
    data = {"a": {"b": None}}
    nset(data, ["a", "b", "c"], 1)
    assert data == {"a": {"b": {"c": 1}}}


def test_nset_replace_primitive_with_dict():
    data = {"a": 1}
    nset(data, ["a", "b"], 2)
    assert data == {"a": {"b": 2}}


def test_nset_replace_primitive_with_list():
    data = {"a": 1}
    nset(data, ["a", 0], 2)
    assert data == {"a": [2]}


def test_nset_with_all_python_basic_types():
    data = {
        "int": 1,
        "float": 2.0,
        "complex": 1 + 2j,
        "str": "string",
        "list": [1, 2, 3],
        "tuple": (4, 5, 6),
        "dict": {"key": "value"},
        "set": {7, 8, 9},
        "frozenset": frozenset([10, 11, 12]),
        "bool": True,
        "none": None,
        "bytes": b"bytes",
        "bytearray": bytearray(b"bytearray"),
    }
    for key in data.keys():
        if isinstance(data[key], (tuple, set, frozenset)):
            with pytest.raises(TypeError):
                nset(data, [key, 0], "new_value")
        elif isinstance(data[key], (list, dict)):
            nset(data, [key, "new_key"], "new_value")
            assert "new_key" in data[key]
        else:
            nset(data, [key, "new_key"], "new_value")
            assert isinstance(data[key], dict) and data[key]["new_key"] == "new_value"


def test_nset_with_custom_classes():
    class CustomList(list):
        pass

    class CustomDict(dict):
        pass

    data = {
        "custom_list": CustomList([1, 2, 3]),
        "custom_dict": CustomDict({"a": 1, "b": 2}),
    }

    nset(data, ["custom_list", 3], 4)
    assert data["custom_list"] == [1, 2, 3, 4]

    nset(data, ["custom_dict", "c"], 3)
    assert data["custom_dict"] == {"a": 1, "b": 2, "c": 3}


def test_nset_with_nested_custom_classes():
    class NestedCustom:
        def __init__(self):
            self.data = {"nested": []}

    data = {"custom": NestedCustom()}
    nset(data, ["custom", "data", "nested", 0], "value")
    assert data["custom"].data["nested"] == ["value"]


@pytest.mark.parametrize(
    "initial, indices, value, expected",
    [
        ({"a": 1}, ["b", 0, "c"], 2, {"a": 1, "b": [{"c": 2}]}),
        ([], [0, "a", 0, "b"], 1, [{"a": [{"b": 1}]}]),
        ({}, ["a", 0, "b", 0, "c"], 1, {"a": [{"b": [{"c": 1}]}]}),
    ],
)
def test_nset_deep_nested_creation(initial, indices, value, expected):
    nset(initial, indices, value)
    assert initial == expected


def test_nset_with_very_large_indices():
    data = {}
    large_indices = list(range(1000))
    nset(data, large_indices, "deep_value")

    current = data
    for i in range(999):
        assert isinstance(current, dict)
        assert i in current
        current = current[i]
    assert current == {999: "deep_value"}


def test_nset_performance_deep_structure(benchmark):
    def deep_insert():
        data = {}
        for i in range(1000):
            nset(data, list(range(i)), i)

    benchmark(deep_insert)


def test_nset_with_duplicate_indices():
    data = {}
    nset(data, ["a", "a", "a"], "value")
    assert data == {"a": {"a": {"a": "value"}}}


def test_nset_replace_existing_structure():
    data = {"a": {"b": {"c": 1}}}
    nset(data, ["a", "b"], "new_value")
    assert data == {"a": {"b": "new_value"}}


def test_nset_with_empty_string_key():
    data = {}
    nset(data, ["", ""], "value")
    assert data == {"": {"": "value"}}


@pytest.mark.parametrize(
    "indices",
    [
        ["a", None, "b"],
        ["a", [], "b"],
        ["a", {}, "b"],
    ],
)
def test_nset_with_invalid_index_types(indices):
    data = {}
    with pytest.raises(TypeError):
        nset(data, indices, "value")


def test_nset_with_boolean_indices():
    data = {}
    nset(data, [True, False], "value")
    assert data == {True: {False: "value"}}


def test_nset_with_float_indices():
    data = {}
    with pytest.raises(TypeError):
        nset(data, [1.5], "value")


@pytest.mark.parametrize(
    "initial, indices, value, expected",
    [
        ({"a": [1, 2]}, ["a", "2"], 3, {"a": [1, 2, 3]}),
        ({"a": {}}, ["a", "0"], "value", {"a": {"0": "value"}}),
    ],
)
def test_nset_string_integer_indices(initial, indices, value, expected):
    nset(initial, indices, value)
    assert initial == expected


def test_nset_with_class_hierarchy():
    class A:
        pass

    class B(A):
        pass

    data = {"a": A(), "b": B()}
    nset(data, ["a", "new_attr"], "value_a")
    nset(data, ["b", "new_attr"], "value_b")

    assert hasattr(data["a"], "new_attr") and data["a"].new_attr == "value_a"
    assert hasattr(data["b"], "new_attr") and data["b"].new_attr == "value_b"


def test_nset_with_property():
    class PropTest:
        @property
        def prop(self):
            return {}

    data = {"obj": PropTest()}
    with pytest.raises(AttributeError):
        nset(data, ["obj", "prop", "new_key"], "value")


def test_nset_with_slots():
    class SlotTest:
        __slots__ = ["x"]

        def __init__(self):
            self.x = {}

    data = {"obj": SlotTest()}
    nset(data, ["obj", "x", "new_key"], "value")
    assert data["obj"].x == {"new_key": "value"}

    with pytest.raises(AttributeError):
        nset(data, ["obj", "y"], "value")


def test_nset_with_defaultdict():
    from collections import defaultdict

    data = defaultdict(list)
    nset(data, ["key", 0], "value")
    assert data == {"key": ["value"]}


def test_nset_with_ordered_dict():
    from collections import OrderedDict

    data = OrderedDict()
    nset(data, ["a", "b", "c"], "value")
    assert list(data.keys()) == ["a"]
    assert data["a"]["b"]["c"] == "value"


@pytest.mark.parametrize(
    "data, indices, value, expected",
    [
        ({"a": 1}, ["a", "b", "c"], 2, {"a": {"b": {"c": 2}}}),
        ({"a": []}, ["a", 0, "b", "c"], 2, {"a": [{"b": {"c": 2}}]}),
        ({}, ["a", 0, "b", 0, "c"], 2, {"a": [{"b": [{"c": 2}]}]}),
    ],
)
def test_nset_create_nested_structures(data, indices, value, expected):
    nset(data, indices, value)
    assert data == expected


def test_nset_with_generator():
    def gen():
        yield 1
        yield 2

    data = {"gen": gen()}
    with pytest.raises(TypeError):
        nset(data, ["gen", 0], 3)


def test_nset_with_bytes():
    data = b"hello"
    with pytest.raises(TypeError):
        nset(data, [5], ord("!"))


def test_nset_with_bytearray():
    data = bytearray(b"hello")
    nset(data, [5], ord("!"))
    assert data == bytearray(b"hello!")


def test_nset_with_memoryview():
    data = memoryview(bytearray(b"hello"))
    with pytest.raises(TypeError):
        nset(data, [5], ord("!"))


@pytest.mark.parametrize(
    "data, indices, value, expected",
    [
        ({"a": range(3)}, ["a", 3], 3, {"a": range(3)}),
        ({"a": range(3)}, ["a", "stop"], 4, {"a": range(3)}),
    ],
)
def test_nset_with_range(data, indices, value, expected):
    nset(data, indices, value)
    assert data == expected


def test_nset_with_circular_reference():
    data = {}
    data["self"] = data
    nset(data, ["self", "new_key"], "value")
    assert data["self"]["new_key"] == "value"
    assert data["self"]["self"]["new_key"] == "value"


def test_nset_with_custom_setitem():
    class CustomSetItem:
        def __init__(self):
            self.data = {}

        def __setitem__(self, key, value):
            self.data[key] = f"custom_{value}"

    data = {"custom": CustomSetItem()}
    nset(data, ["custom", "key"], "value")
    assert data["custom"].data == {"key": "custom_value"}


def test_nset_with_namedtuple():
    from collections import namedtuple

    Point = namedtuple("Point", ["x", "y"])
    data = {"point": Point(1, 2)}
    with pytest.raises(AttributeError):
        nset(data, ["point", "x"], 3)


def test_nset_with_enum():
    from enum import Enum

    class Color(Enum):
        RED = 1
        GREEN = 2

    data = {"color": Color.RED}
    with pytest.raises(AttributeError):
        nset(data, ["color", "value"], 3)


def test_nset_with_large_list(benchmark):
    def set_large_list():
        data = list(range(10**5))
        nset(data, [10**5], "end")

    benchmark(set_large_list)


def test_nset_with_complex_keys():
    data = {}
    complex_key = complex(1, 2)
    nset(data, [complex_key, "nested"], "value")
    assert data == {complex_key: {"nested": "value"}}


def test_nset_with_callable_objects():
    def func():
        pass

    data = {"func": func}
    nset(data, ["func", "attribute"], "value")
    assert hasattr(func, "attribute")
    assert func.attribute == "value"


# File: tests/test_nset.py
