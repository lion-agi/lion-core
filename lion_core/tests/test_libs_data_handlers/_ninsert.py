import pytest
from lion_core.libs.data_handlers._ninsert import ninsert


@pytest.mark.parametrize(
    "data, indices, value, expected",
    [
        ({"a": {"b": [1, 2]}}, ["a", "b", 2], 3, {"a": {"b": [1, 2, 3]}}),
        ([1, [2, 3]], [1, 2], 4, [1, [2, 3, 4]]),
        ({"a": [1, {"b": 2}]}, ["a", 1, "c"], 3, {"a": [1, {"b": 2, "c": 3}]}),
        ({}, ["a", "b", "c"], 1, {"a": {"b": {"c": 1}}}),
        ({"a": {"b": 2}}, ["a", "b"], 3, {"a": {"b": 3}}),
        (
            {"a": {"b": [1, 2]}},
            ["a", "b", 5],
            3,
            {"a": {"b": [1, 2, None, None, None, 3]}},
        ),
        ([], [0, "a"], 1, [{"a": 1}]),
        ({"a": []}, ["a", 0, "b"], 1, {"a": [{"b": 1}]}),
    ],
)
def test_ninsert_valid_cases(data, indices, value, expected):
    ninsert(data, indices, value)
    assert data == expected


def test_ninsert_empty_indices():
    data = {"a": 1}
    with pytest.raises(ValueError, match="Indices list cannot be empty"):
        ninsert(data, [], 2)


@pytest.mark.parametrize(
    "data, indices, value",
    [
        ([1, 2, 3], ["a"], 4),
        ({"a": 1}, [0], 2),
        ({"a": {"b": 2}}, ["a", "b", "c"], 3),
    ],
)
def test_ninsert_type_errors(data, indices, value):
    with pytest.raises(TypeError):
        ninsert(data, indices, value)


def test_ninsert_nested_creation():
    data = {}
    ninsert(data, ["a", 0, "b", 1, "c"], 42)
    assert data == {"a": [{"b": [None, {"c": 42}]}]}


def test_ninsert_overwrite_existing():
    data = {"a": {"b": {"c": 1}}}
    ninsert(data, ["a", "b", "c"], 2)
    assert data == {"a": {"b": {"c": 2}}}


def test_ninsert_extend_list():
    data = {"a": [1, 2]}
    ninsert(data, ["a", 5], 3)
    assert data == {"a": [1, 2, None, None, None, 3]}


def test_ninsert_with_tuple():
    data = {"a": (1, 2)}
    with pytest.raises(TypeError):
        ninsert(data, ["a", 2], 3)


def test_ninsert_with_set():
    data = {"a": {1, 2}}
    with pytest.raises(TypeError):
        ninsert(data, ["a", 3], 3)


def test_ninsert_with_none():
    data = {"a": None}
    ninsert(data, ["a", "b"], 1)
    assert data == {"a": {"b": 1}}


def test_ninsert_with_custom_object():
    class CustomObj:
        def __init__(self):
            self.data = {}

        def __setitem__(self, key, value):
            self.data[key] = value

    obj = CustomObj()
    ninsert(obj, ["data", "key"], "value")
    assert obj.data == {"key": "value"}


def test_ninsert_with_property():
    class PropObj:
        def __init__(self):
            self._data = {}

        @property
        def data(self):
            return self._data

    obj = PropObj()
    with pytest.raises(AttributeError):
        ninsert(obj, ["data", "key"], "value")


def test_ninsert_with_large_nested_structure():
    data = {}
    for i in range(1000):
        ninsert(data, ["level" + str(i)], i)
    assert data["level999"] == 999


def test_ninsert_performance_with_large_list(benchmark):
    def insert_many():
        data = []
        for i in range(10**5):
            ninsert(data, [i], i)

    benchmark(insert_many)


@pytest.mark.parametrize(
    "data, indices, value, expected",
    [
        ({"a": 1}, ["b", "c"], 2, {"a": 1, "b": {"c": 2}}),
        ([1, 2], [2, "a"], 3, [1, 2, {"a": 3}]),
        ({}, ["a", 0, "b"], 1, {"a": [{"b": 1}]}),
    ],
)
def test_ninsert_create_intermediate_structures(data, indices, value, expected):
    ninsert(data, indices, value)
    assert data == expected


def test_ninsert_with_negative_list_index():
    data = [1, 2, 3]
    with pytest.raises(ValueError, match="list index cannot be negative"):
        ninsert(data, [-1], 4)


def test_ninsert_with_string_key_for_list():
    data = [1, 2, 3]
    with pytest.raises(TypeError, match="Cannot use non-integer index on a list"):
        ninsert(data, ["key"], 4)


def test_ninsert_with_int_key_for_dict():
    data = {}
    ninsert(data, [1], "value")
    assert data == {1: "value"}


def test_ninsert_with_existing_none_value():
    data = {"a": {"b": None}}
    ninsert(data, ["a", "b", "c"], 1)
    assert data == {"a": {"b": {"c": 1}}}


def test_ninsert_replace_primitive_with_dict():
    data = {"a": 1}
    ninsert(data, ["a", "b"], 2)
    assert data == {"a": {"b": 2}}


def test_ninsert_replace_primitive_with_list():
    data = {"a": 1}
    ninsert(data, ["a", 0], 2)
    assert data == {"a": [2]}


def test_ninsert_with_all_python_basic_types():
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
                ninsert(data, [key, 0], "new_value")
        elif isinstance(data[key], (list, dict)):
            ninsert(data, [key, "new_key"], "new_value")
            assert "new_key" in data[key]
        else:
            ninsert(data, [key, "new_key"], "new_value")
            assert isinstance(data[key], dict) and data[key]["new_key"] == "new_value"


def test_ninsert_with_custom_classes():
    class CustomList(list):
        pass

    class CustomDict(dict):
        pass

    data = {
        "custom_list": CustomList([1, 2, 3]),
        "custom_dict": CustomDict({"a": 1, "b": 2}),
    }

    ninsert(data, ["custom_list", 3], 4)
    assert data["custom_list"] == [1, 2, 3, 4]

    ninsert(data, ["custom_dict", "c"], 3)
    assert data["custom_dict"] == {"a": 1, "b": 2, "c": 3}


def test_ninsert_with_nested_custom_classes():
    class NestedCustom:
        def __init__(self):
            self.data = {"nested": []}

    data = {"custom": NestedCustom()}
    ninsert(data, ["custom", "data", "nested", 0], "value")
    assert data["custom"].data["nested"] == ["value"]


@pytest.mark.parametrize(
    "initial, indices, value, expected",
    [
        ({"a": 1}, ["b", 0, "c"], 2, {"a": 1, "b": [{"c": 2}]}),
        ([], [0, "a", 0, "b"], 1, [{"a": [{"b": 1}]}]),
        ({}, ["a", 0, "b", 0, "c"], 1, {"a": [{"b": [{"c": 1}]}]}),
    ],
)
def test_ninsert_deep_nested_creation(initial, indices, value, expected):
    ninsert(initial, indices, value)
    assert initial == expected


def test_ninsert_with_very_large_indices():
    data = {}
    large_indices = list(range(1000))
    ninsert(data, large_indices, "deep_value")

    current = data
    for i in range(999):
        assert isinstance(current, dict)
        assert i in current
        current = current[i]
    assert current == {"999": "deep_value"}


def test_ninsert_performance_deep_structure(benchmark):
    def deep_insert():
        data = {}
        for i in range(1000):
            ninsert(data, list(range(i)), i)

    benchmark(deep_insert)


def test_ninsert_with_duplicate_indices():
    data = {}
    ninsert(data, ["a", "a", "a"], "value")
    assert data == {"a": {"a": {"a": "value"}}}


def test_ninsert_replace_existing_structure():
    data = {"a": {"b": {"c": 1}}}
    ninsert(data, ["a", "b"], "new_value")
    assert data == {"a": {"b": "new_value"}}


def test_ninsert_with_empty_string_key():
    data = {}
    ninsert(data, ["", ""], "value")
    assert data == {"": {"": "value"}}


@pytest.mark.parametrize(
    "indices",
    [
        ["a", None, "b"],
        ["a", [], "b"],
        ["a", {}, "b"],
    ],
)
def test_ninsert_with_invalid_index_types(indices):
    data = {}
    with pytest.raises(TypeError):
        ninsert(data, indices, "value")


def test_ninsert_with_boolean_indices():
    data = {}
    ninsert(data, [True, False], "value")
    assert data == {True: {False: "value"}}


def test_ninsert_with_float_indices():
    data = {}
    with pytest.raises(TypeError):
        ninsert(data, [1.5], "value")


@pytest.mark.parametrize(
    "initial, indices, value, expected",
    [
        ({"a": [1, 2]}, ["a", "2"], 3, {"a": [1, 2, 3]}),
        ({"a": {}}, ["a", "0"], "value", {"a": {"0": "value"}}),
    ],
)
def test_ninsert_string_integer_indices(initial, indices, value, expected):
    ninsert(initial, indices, value)
    assert initial == expected


def test_ninsert_with_class_hierarchy():
    class A:
        pass

    class B(A):
        pass

    data = {"a": A(), "b": B()}
    ninsert(data, ["a", "new_attr"], "value_a")
    ninsert(data, ["b", "new_attr"], "value_b")

    assert hasattr(data["a"], "new_attr") and data["a"].new_attr == "value_a"
    assert hasattr(data["b"], "new_attr") and data["b"].new_attr == "value_b"


def test_ninsert_with_property():
    class PropTest:
        @property
        def prop(self):
            return {}

    data = {"obj": PropTest()}
    with pytest.raises(AttributeError):
        ninsert(data, ["obj", "prop", "new_key"], "value")


def test_ninsert_with_slots():
    class SlotTest:
        __slots__ = ["x"]

        def __init__(self):
            self.x = {}

    data = {"obj": SlotTest()}
    ninsert(data, ["obj", "x", "new_key"], "value")
    assert data["obj"].x == {"new_key": "value"}

    with pytest.raises(AttributeError):
        ninsert(data, ["obj", "y"], "value")


def test_ninsert_with_defaultdict():
    from collections import defaultdict

    data = defaultdict(list)
    ninsert(data, ["key", 0], "value")
    assert data == {"key": ["value"]}


def test_ninsert_with_ordered_dict():
    from collections import OrderedDict

    data = OrderedDict()
    ninsert(data, ["a", "b", "c"], "value")
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
def test_ninsert_create_nested_structures(data, indices, value, expected):
    ninsert(data, indices, value)
    assert data == expected


def test_ninsert_with_generator():
    def gen():
        yield 1
        yield 2

    data = {"gen": gen()}
    with pytest.raises(TypeError):
        ninsert(data, ["gen", 0], 3)


def test_ninsert_with_bytes():
    data = b"hello"
    with pytest.raises(TypeError):
        ninsert(data, [5], ord("!"))


def test_ninsert_with_bytearray():
    data = bytearray(b"hello")
    ninsert(data, [5], ord("!"))
    assert data == bytearray(b"hello!")


def test_ninsert_with_memoryview():
    data = memoryview(bytearray(b"hello"))
    with pytest.raises(TypeError):
        ninsert(data, [5], ord("!"))


@pytest.mark.parametrize(
    "data, indices, value, expected",
    [
        ({"a": range(3)}, ["a", 3], 3, {"a": range(3)}),
        ({"a": range(3)}, ["a", "stop"], 4, {"a": range(3)}),
    ],
)
def test_ninsert_with_range(data, indices, value, expected):
    ninsert(data, indices, value)
    assert data == expected


def test_ninsert_with_circular_reference():
    data = {}
    data["self"] = data
    ninsert(data, ["self", "new_key"], "value")
    assert data["self"]["new_key"] == "value"
    assert data["self"]["self"]["new_key"] == "value"


# File: tests/test_ninsert.py
