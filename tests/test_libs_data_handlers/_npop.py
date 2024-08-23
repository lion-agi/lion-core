import pytest

from lion_core.libs.data_handlers._npop import npop
from lion_core.setting import LN_UNDEFINED


@pytest.mark.parametrize(
    "data, indices, expected_result, expected_data",
    [
        ({"a": {"b": {"c": 3}}}, ["a", "b", "c"], 3, {"a": {"b": {}}}),
        ({"a": {"b": [1, 2, 3]}}, ["a", "b", 2], 3, {"a": {"b": [1, 2]}}),
        ({"a": [1, {"b": 2}]}, ["a", 1, "b"], 2, {"a": [1, {}]}),
        ({"a": 1, "b": 2}, ["b"], 2, {"a": 1}),
        ([1, [2, [3, 4]], 5], [1, 1, 0], 3, [1, [2, [4]], 5]),
        (
            {"key with spaces": {"nested": "value"}},
            ["key with spaces", "nested"],
            "value",
            {"key with spaces": {}},
        ),
        ({0: "zero", 1: "one"}, [1], "one", {0: "zero"}),
        ({"a": {"b": None}}, ["a", "b"], None, {"a": {}}),
        ({"": {"nested": "value"}}, ["", "nested"], "value", {"": {}}),
        ({True: "true", False: "false"}, [True], "true", {False: "false"}),
        ({(1, 2): "tuple key"}, [(1, 2)], "tuple key", {}),
        (
            {"a": {"b": {"c": {"d": 1}}}},
            ["a", "b", "c", "d"],
            1,
            {"a": {"b": {"c": {}}}},
        ),
    ],
)
def test_npop_various_scenarios(data, indices, expected_result, expected_data):
    assert npop(data, indices) == expected_result
    assert data == expected_data


@pytest.mark.parametrize(
    "data, indices, default, expected_result, expected_data",
    [
        ({"a": {"b": 2}}, ["a", "c"], 10, 10, {"a": {"b": 2}}),
        ([], [0], "default", "default", []),
        ({}, ["non_existent"], None, None, {}),
        ({"a": 1}, ["b"], LN_UNDEFINED, LN_UNDEFINED, {"a": 1}),
    ],
)
def test_npop_with_default(
    data, indices, default, expected_result, expected_data
):
    assert npop(data, indices, default=default) == expected_result
    assert data == expected_data


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
def test_npop_raises_key_error(data, indices):
    with pytest.raises(KeyError):
        npop(data, indices)


@pytest.mark.parametrize(
    "data, indices",
    [
        ([1, 2, 3], ["a"]),
        ({"a": 1}, [0]),
        ({"a": [1, 2, 3]}, ["a", "b"]),
    ],
)
def test_npop_raises_type_error(data, indices):
    with pytest.raises(TypeError):
        npop(data, indices)


def test_npop_empty_indices():
    data = {"a": 1}
    with pytest.raises(ValueError, match="Indices list cannot be empty"):
        npop(data, [])


def test_npop_none_data():
    with pytest.raises(TypeError):
        npop(None, ["a"])


def test_npop_non_subscriptable():
    with pytest.raises(TypeError):
        npop(42, [0])


def test_npop_with_zero_index():
    data = [1, 2, 3]
    assert npop(data, [0]) == 1
    assert data == [2, 3]


def test_npop_with_negative_index():
    data = [1, 2, 3]
    with pytest.raises(ValueError):
        npop(data, [-1])


def test_npop_with_string_index_for_list():
    data = [1, 2, 3]
    with pytest.raises(TypeError):
        npop(data, ["0"])


def test_npop_with_int_index_for_dict():
    data = {"0": "value"}
    assert npop(data, ["0"]) == "value"
    assert data == {}


def test_npop_with_nested_default_dict():
    from collections import defaultdict

    data = defaultdict(lambda: defaultdict(int))
    data["a"]["b"] = 1
    assert npop(data, ["a", "b"]) == 1
    assert dict(data) == {"a": {}}


def test_npop_with_custom_object():
    class CustomObj:
        def __init__(self):
            self.attr = {"key": "value"}

        def __getitem__(self, key):
            return self.attr[key]

        def __delitem__(self, key):
            del self.attr[key]

    obj = CustomObj()
    assert npop(obj, ["key"]) == "value"
    assert obj.attr == {}


def test_npop_with_property():
    class PropObj:
        def __init__(self):
            self._data = {"key": "value"}

        @property
        def data(self):
            return self._data

    obj = PropObj()
    assert npop(obj.data, ["key"]) == "value"
    assert obj._data == {}


@pytest.mark.parametrize(
    "data, indices, expected_result, expected_data",
    [
        ({"a": 1, "b": 2, "c": 3}, ["a", "b", "c"], 3, {"a": 1, "b": 2}),
        ([1, 2, [3, 4, [5, 6]]], [2, 2, 1], 6, [1, 2, [3, 4, [5]]]),
        (
            {"a": [{"b": {"c": [1, 2, 3]}}]},
            ["a", 0, "b", "c", 2],
            3,
            {"a": [{"b": {"c": [1, 2]}}]},
        ),
    ],
)
def test_npop_long_paths(data, indices, expected_result, expected_data):
    assert npop(data, indices) == expected_result
    assert data == expected_data


def test_npop_with_large_nested_structure():
    large_data = {"level1": {}}
    current = large_data["level1"]
    for i in range(2, 101):
        current[f"level{i}"] = {}
        current = current[f"level{i}"]
    current["value"] = "deep"

    indices = [f"level{i}" for i in range(1, 101)] + ["value"]
    assert npop(large_data, indices) == "deep"

    # Verify the structure is empty
    current = large_data["level1"]
    for i in range(2, 101):
        assert current == {}
        if f"level{i}" in current:
            current = current[f"level{i}"]


def test_npop_performance_with_large_list(benchmark):
    large_list = list(range(10**5))

    def pop_last():
        return npop(large_list, [-1])

    result = benchmark(pop_last)
    assert result == 99999
    assert len(large_list) == 99999


def test_npop_with_all_python_basic_types():
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
    for key in list(data.keys()):
        assert npop(data, [key]) == data[key]
    assert data == {}


@pytest.mark.parametrize(
    "data, indices, expected_result, expected_data",
    [
        ({"a": {"b": {"c": 3}}}, "a.b.c", 3, {"a": {"b": {}}}),
        ([1, [2, [3, 4]]], "1.1.0", 3, [1, [2, [4]]]),
        ({"a": [1, {"b": 2}]}, "a.1.b", 2, {"a": [1, {}]}),
    ],
)
def test_npop_with_string_indices(
    data, indices, expected_result, expected_data
):
    assert npop(data, indices.split(".")) == expected_result
    assert data == expected_data


def test_npop_with_generator():
    def gen():
        yield 1
        yield 2
        yield 3

    data = {"gen": gen()}
    with pytest.raises(TypeError):
        npop(data, ["gen", 1])


def test_npop_with_recursive_structure():
    data = {"a": 1}
    data["b"] = data
    assert npop(data, ["a"]) == 1
    assert data == {"b": {"b": {...}}}


def test_npop_with_custom_classes():
    class CustomList(list):
        pass

    class CustomDict(dict):
        pass

    data = CustomDict({"a": CustomList([1, 2, 3])})
    assert npop(data, ["a", 1]) == 2
    assert data == CustomDict({"a": CustomList([1, 3])})


# File: tests/test_npop.py
