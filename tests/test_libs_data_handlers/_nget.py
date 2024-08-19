import pytest
from lion_core.libs.data_handlers._nget import nget
from lion_core.setting import LN_UNDEFINED


@pytest.mark.parametrize(
    "data, indices, expected",
    [
        ({"a": {"b": {"c": 3}}}, ["a", "b", "c"], 3),
        ([1, [2, [3, 4]]], [1, 1, 0], 3),
        ({"a": [1, {"b": 2}]}, ["a", 1, "b"], 2),
        ({"a": 1, "b": 2}, ["b"], 2),
        ({"a": {"b": [{"c": 1}, {"c": 2}]}}, ["a", "b", 1, "c"], 2),
        ({"a": {"b": {"c": {"d": {"e": 5}}}}}, ["a", "b", "c", "d", "e"], 5),
        ([[[1]]], [0, 0, 0], 1),
        ({"a": [1, 2, {"b": [3, 4, {"c": 5}]}]}, ["a", 2, "b", 2, "c"], 5),
    ],
)
def test_nget_valid_paths(data, indices, expected):
    assert nget(data, indices) == expected


@pytest.mark.parametrize(
    "data, indices, default, expected",
    [
        ({"a": {"b": 2}}, ["a", "c"], 10, 10),
        ({"a": [1, 2, 3]}, [0, 1], "default", "default"),
        ({}, ["a", "b"], None, None),
        ([], [0], LN_UNDEFINED, LN_UNDEFINED),
    ],
)
def test_nget_with_default(data, indices, default, expected):
    assert nget(data, indices, default) == expected


@pytest.mark.parametrize(
    "data, indices",
    [
        ({}, ["a"]),
        ([], [0]),
        ({"a": {"b": 2}}, ["a", "c"]),
        ([1, 2, 3], [3]),
        ({"a": [1, 2]}, ["a", 2]),
        ({"a": {"b": 1}}, ["a", "b", "c"]),
    ],
)
def test_nget_raises_lookup_error(data, indices):
    with pytest.raises(LookupError):
        nget(data, indices)


@pytest.mark.parametrize(
    "data, indices",
    [
        ([1, 2, 3], ["a"]),
        ({"a": 1}, [0]),
        ({"a": [1, 2, 3]}, ["a", "b"]),
    ],
)
def test_nget_raises_type_error(data, indices):
    with pytest.raises(LookupError):
        nget(data, indices)


def test_nget_empty_indices():
    with pytest.raises(ValueError, match="Indices list cannot be empty"):
        nget({"a": 1}, [])


def test_nget_none_data():
    with pytest.raises(TypeError):
        nget(None, ["a"])


def test_nget_non_subscriptable():
    with pytest.raises(LookupError):
        nget(42, [0])


def test_nget_with_zero_index():
    data = [1, 2, 3]
    assert nget(data, [0]) == 1


def test_nget_with_negative_index():
    data = [1, 2, 3]
    with pytest.raises(LookupError):
        nget(data, [-1])


def test_nget_with_string_index_for_list():
    data = [1, 2, 3]
    with pytest.raises(LookupError):
        nget(data, ["0"])


def test_nget_with_int_index_for_dict():
    data = {"0": "value"}
    assert nget(data, ["0"]) == "value"


def test_nget_with_nested_default_dict():
    from collections import defaultdict

    data = defaultdict(lambda: defaultdict(int))
    data["a"]["b"] = 1
    assert nget(data, ["a", "b"]) == 1
    assert nget(data, ["a", "c"]) == 0


def test_nget_with_custom_object():
    class CustomObj:
        def __init__(self):
            self.attr = {"key": "value"}

        def __getitem__(self, key):
            return self.attr[key]

    obj = CustomObj()
    assert nget(obj, ["key"]) == "value"


def test_nget_with_property():
    class PropObj:
        @property
        def prop(self):
            return {"key": "value"}

    obj = PropObj()
    assert nget(obj, ["prop", "key"]) == "value"


@pytest.mark.parametrize(
    "data, indices, expected",
    [
        ({"a": 1, "b": 2, "c": 3}, ["a", "b", "c"], 3),
        ([1, 2, [3, 4, [5, 6]]], [2, 2, 1], 6),
        ({"a": [{"b": {"c": [1, 2, 3]}}]}, ["a", 0, "b", "c", 2], 3),
    ],
)
def test_nget_long_paths(data, indices, expected):
    assert nget(data, indices) == expected


def test_nget_with_large_nested_structure():
    large_data = {"level1": {}}
    current = large_data["level1"]
    for i in range(2, 101):
        current[f"level{i}"] = {}
        current = current[f"level{i}"]
    current["value"] = "deep"

    indices = [f"level{i}" for i in range(1, 101)] + ["value"]
    assert nget(large_data, indices) == "deep"


def test_nget_performance_with_large_list(benchmark):
    large_list = list(range(10**6))

    def fetch_last():
        return nget(large_list, [-1])

    result = benchmark(fetch_last)
    assert result == 999999


def test_nget_with_all_python_basic_types():
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
        assert nget(data, [key]) == data[key]


@pytest.mark.parametrize(
    "data, indices, expected",
    [
        ({"a": {"b": {"c": 3}}}, "a.b.c", 3),
        ([1, [2, [3, 4]]], "1.1.0", 3),
        ({"a": [1, {"b": 2}]}, "a.1.b", 2),
    ],
)
def test_nget_with_string_indices(data, indices, expected):
    assert nget(data, indices.split(".")) == expected


# File: tests/test_nget.py
