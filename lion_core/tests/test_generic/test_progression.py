import pytest
from typing import Any
from collections import deque
import asyncio
import random
import string

from lion_core.generic.progression import Progression, prog
from lion_core.generic.element import Element
from lion_core.exceptions import ItemNotFoundError
from lion_core.sys_utils import SysUtil


class MockElement(Element):
    value: Any


@pytest.fixture
def sample_elements():
    return [MockElement(value=i) for i in range(5)]


@pytest.fixture
def sample_progression(sample_elements):
    return Progression(order=[e.ln_id for e in sample_elements])


def generate_random_string(length: int) -> str:
    return "".join(random.choices(string.ascii_letters + string.digits, k=length))


@pytest.mark.parametrize(
    "input_data",
    [
        [],
        [1, 2, 3],
        ["a", "b", "c"],
        [MockElement(value=i) for i in range(3)],
    ],
)
def test_initialization(input_data):
    prog = Progression(order=input_data)
    assert len(prog) == len(input_data)
    for item in input_data:
        assert SysUtil.get_id(item) in prog.order


def test_initialization_with_name():
    name = "test_progression"
    prog = Progression(order=[1, 2, 3], name=name)
    assert prog.name == name


def test_contains(sample_progression, sample_elements):
    for element in sample_elements:
        assert element in sample_progression
        assert element.ln_id in sample_progression


def test_not_contains(sample_progression):
    assert "non_existent_id" not in sample_progression
    assert MockElement(value="new") not in sample_progression


def test_list_conversion(sample_progression, sample_elements):
    prog_list = sample_progression.__list__()
    assert isinstance(prog_list, list)
    assert len(prog_list) == len(sample_elements)
    assert all(isinstance(item, str) for item in prog_list)


def test_len(sample_progression, sample_elements):
    assert len(sample_progression) == len(sample_elements)


@pytest.mark.parametrize(
    "index, expected_type",
    [
        (0, str),
        (slice(0, 2), Progression),
    ],
)
def test_getitem(sample_progression, index, expected_type):
    result = sample_progression[index]
    assert isinstance(result, expected_type)


def test_getitem_out_of_range(sample_progression):
    with pytest.raises(ItemNotFoundError):
        _ = sample_progression[len(sample_progression)]


def test_setitem(sample_progression):
    new_element = MockElement(value="new")
    sample_progression[0] = new_element
    assert sample_progression[0] == new_element.ln_id


def test_setitem_slice(sample_progression):
    new_elements = [MockElement(value=f"new_{i}") for i in range(2)]
    sample_progression[0:2] = new_elements
    assert sample_progression[0] == new_elements[0].ln_id
    assert sample_progression[1] == new_elements[1].ln_id


def test_delitem(sample_progression):
    original_length = len(sample_progression)
    del sample_progression[0]
    assert len(sample_progression) == original_length - 1


def test_delitem_slice(sample_progression):
    original_length = len(sample_progression)
    del sample_progression[0:2]
    assert len(sample_progression) == original_length - 2


def test_iter(sample_progression, sample_elements):
    for prog_item, element in zip(sample_progression, sample_elements):
        assert prog_item == element.ln_id


def test_next(sample_progression, sample_elements):
    assert next(sample_progression) == sample_elements[0].ln_id


def test_next_empty():
    empty_prog = Progression()
    with pytest.raises(StopIteration):
        next(empty_prog)


def test_size(sample_progression, sample_elements):
    assert sample_progression.size() == len(sample_elements)


def test_clear(sample_progression):
    sample_progression.clear()
    assert len(sample_progression) == 0


@pytest.mark.parametrize(
    "input_item",
    [
        MockElement(value="new"),
        "new_id",
        ["id1", "id2"],
        [MockElement(value="new1"), MockElement(value="new2")],
    ],
)
def test_append(sample_progression, input_item):
    original_length = len(sample_progression)
    sample_progression.append(input_item)
    assert len(sample_progression) > original_length

    if isinstance(input_item, list):
        for item in input_item:
            assert SysUtil.get_id(item) in sample_progression
    else:
        assert SysUtil.get_id(input_item) in sample_progression


def test_pop(sample_progression):
    original_length = len(sample_progression)
    popped_item = sample_progression.pop()
    assert len(sample_progression) == original_length - 1
    assert popped_item not in sample_progression


def test_pop_with_index(sample_progression):
    original_first_item = sample_progression[0]
    popped_item = sample_progression.pop(0)
    assert popped_item == original_first_item
    assert popped_item not in sample_progression


def test_pop_empty():
    empty_prog = Progression()
    with pytest.raises(ItemNotFoundError):
        empty_prog.pop()


@pytest.mark.parametrize(
    "input_item",
    [
        MockElement(value="new"),
        "new_id",
        ["id1", "id2"],
        [MockElement(value="new1"), MockElement(value="new2")],
    ],
)
def test_include(sample_progression, input_item):
    original_length = len(sample_progression)
    sample_progression.include(input_item)
    assert len(sample_progression) > original_length

    if isinstance(input_item, list):
        for item in input_item:
            assert SysUtil.get_id(item) in sample_progression
    else:
        assert SysUtil.get_id(input_item) in sample_progression


@pytest.mark.parametrize(
    "input_item",
    [
        MockElement(value="new"),
        "new_id",
        ["id1", "id2"],
        [MockElement(value="new1"), MockElement(value="new2")],
    ],
)
def test_exclude(sample_progression, input_item):
    sample_progression.include(input_item)
    original_length = len(sample_progression)
    sample_progression.exclude(input_item)
    assert len(sample_progression) < original_length

    if isinstance(input_item, list):
        for item in input_item:
            assert SysUtil.get_id(item) not in sample_progression
    else:
        assert SysUtil.get_id(input_item) not in sample_progression


def test_is_empty(sample_progression):
    assert not sample_progression.is_empty()
    sample_progression.clear()
    assert sample_progression.is_empty()


def test_reverse():
    prog = Progression(order=[1, 2, 3])
    reversed_prog = prog.__reverse__()
    assert list(reversed_prog) == ["3", "2", "1"]


def test_equality():
    prog1 = Progression(order=[1, 2, 3], name="test")
    prog2 = Progression(order=[1, 2, 3], name="test")
    prog3 = Progression(order=[1, 2, 3], name="different")
    prog4 = Progression(order=[3, 2, 1], name="test")

    assert prog1 == prog2
    assert prog1 != prog3
    assert prog1 != prog4


def test_index():
    prog = Progression(order=[1, 2, 3, 2])
    assert prog.index(2) == 1
    assert prog.index(2, 2) == 3
    with pytest.raises(ValueError):
        prog.index(4)


def test_remove(sample_progression, sample_elements):
    to_remove = sample_elements[2]
    sample_progression.remove(to_remove)
    assert to_remove not in sample_progression


def test_remove_non_existent(sample_progression):
    with pytest.raises(ItemNotFoundError):
        sample_progression.remove("non_existent_id")


def test_popleft(sample_progression, sample_elements):
    first_element = sample_elements[0]
    popped = sample_progression.popleft()
    assert popped == first_element.ln_id
    assert first_element not in sample_progression


def test_popleft_empty():
    empty_prog = Progression()
    with pytest.raises(ItemNotFoundError):
        empty_prog.popleft()


def test_extend():
    prog1 = Progression(order=[1, 2])
    prog2 = Progression(order=[3, 4])
    prog1.extend(prog2)
    assert list(prog1) == ["1", "2", "3", "4"]


def test_extend_non_progression():
    prog = Progression(order=[1, 2])
    with pytest.raises(TypeError):
        prog.extend([3, 4])


def test_count():
    prog = Progression(order=[1, 2, 2, 3, 2])
    assert prog.count(2) == 3
    assert prog.count(4) == 0


@pytest.mark.parametrize(
    "input_data, expected",
    [
        ([], False),
        ([1, 2, 3], True),
    ],
)
def test_bool(input_data, expected):
    prog = Progression(order=input_data)
    assert bool(prog) == expected


def test_add():
    prog1 = Progression(order=[1, 2])
    prog2 = prog1 + [3, 4]
    assert isinstance(prog2, Progression)
    assert list(prog2) == ["1", "2", "3", "4"]


def test_radd():
    prog = Progression(order=[2, 3])
    result = [1] + prog
    assert isinstance(result, Progression)
    assert list(result) == ["1", "2", "3"]


def test_iadd():
    prog = Progression(order=[1, 2])
    prog += [3, 4]
    assert list(prog) == ["1", "2", "3", "4"]


def test_isub():
    prog = Progression(order=[1, 2, 3, 4])
    prog -= [2, 4]
    assert list(prog) == ["1", "3"]


def test_sub():
    prog1 = Progression(order=[1, 2, 3, 4])
    prog2 = prog1 - [2, 4]
    assert isinstance(prog2, Progression)
    assert list(prog2) == ["1", "3"]


def test_insert():
    prog = Progression(order=[1, 3])
    prog.insert(1, 2)
    assert list(prog) == ["1", "2", "3"]


def test_insert_multiple():
    prog = Progression(order=[1, 4])
    prog.insert(1, [2, 3])
    assert list(prog) == ["1", "2", "3", "4"]


@pytest.mark.parametrize("size", [10, 100, 1000])
def test_large_progression(size):
    large_prog = Progression(order=range(size))
    assert len(large_prog) == size
    assert large_prog.size() == size
    assert large_prog[size // 2] == str(size // 2)


def test_concurrent_operations():
    prog = Progression()

    async def add_items():
        for _ in range(100):
            prog.append(MockElement(value=generate_random_string(10)))
            await asyncio.sleep(0.01)

    async def remove_items():
        for _ in range(50):
            if not prog.is_empty():
                prog.pop()
            await asyncio.sleep(0.02)

    async def run_concurrent():
        await asyncio.gather(add_items(), remove_items())

    asyncio.run(run_concurrent())
    assert 50 <= len(prog) <= 100


def test_progression_with_custom_elements():
    class CustomElement(Element):
        data: dict

    elements = [CustomElement(data={"value": i}) for i in range(5)]
    prog = Progression(order=elements)
    assert len(prog) == 5
    for element in elements:
        assert element in prog


def test_progression_serialization():
    prog = Progression(order=[1, 2, 3], name="test_prog")
    serialized = prog.to_dict()
    deserialized = Progression.from_dict(serialized)
    assert deserialized == prog
    assert deserialized.name == prog.name


def test_progression_deep_copy():
    import copy

    prog = Progression(order=[1, 2, 3], name="test_prog")
    prog_copy = copy.deepcopy(prog)
    assert prog == prog_copy
    assert prog is not prog_copy


@pytest.mark.parametrize("input_type", [list, tuple, set, deque])
def test_progression_from_various_types(input_type):
    data = input_type([1, 2, 3])
    prog = Progression(order=data)
    assert len(prog) == 3
    assert list(prog) == ["1", "2", "3"]


def test_progression_with_duplicate_items():
    prog = Progression(order=[1, 2, 2, 3, 1])
    assert len(prog) == 5
    assert list(prog) == ["1", "2", "2", "3", "1"]
    assert prog.count(2) == 2


def test_progression_slice_assignment():
    prog = Progression(order=[1, 2, 3, 4, 5])
    prog[1:4] = [6, 7]
    assert list(prog) == ["1", "6", "7", "5"]


def test_progression_reverse_iteration():
    prog = Progression(order=[1, 2, 3])
    assert list(reversed(prog)) == ["3", "2", "1"]


def test_progression_exception_handling():
    prog = Progression(order=[1, 2, 3])
    with pytest.raises(IndexError):
        prog[10]
    with pytest.raises(ValueError):
        prog.remove(4)
    with pytest.raises(TypeError):
        prog.extend([1, 2, 3])  # Should be a Progression, not a list


def test_progression_memory_usage():
    import sys

    small_prog = Progression(order=range(10))
    large_prog = Progression(order=range(10000))
    small_size = sys.getsizeof(small_prog)
    large_size = sys.getsizeof(large_prog)
    assert large_size > small_size
    # Ensure memory usage grows sub-linearly
    assert large_size < small_size * 1000


def test_prog_function():
    p = prog([1, 2, 3], name="test")
    assert isinstance(p, Progression)
    assert p.name == "test"
    assert list(p) == ["1", "2", "3"]


def test_progression_with_generator():
    def gen():
        for i in range(5):
            yield i

    p = Progression(order=gen())
    assert len(p) == 5
    assert list(p) == ["0", "1", "2", "3", "4"]


def test_progression_with_async_generator():
    import asyncio

    async def async_gen():
        for i in range(5):
            await asyncio.sleep(0.1)
            yield i

    async def run_test():
        p = Progression(order=[i async for i in async_gen()])
        assert len(p) == 5
        assert list(p) == ["0", "1", "2", "3", "4"]

    asyncio.run(run_test())


def test_progression_with_invalid_order():
    with pytest.raises(ValueError):
        Progression(order=42)  # Integer is not iterable


def test_progression_with_mixed_types():
    p = Progression(order=[1, "two", MockElement(value=3), 4.0])
    assert len(p) == 4
    assert isinstance(p[0], str)
    assert isinstance(p[1], str)
    assert len(p[2]) == 28  # Assuming ln_id is 28 characters long
    assert isinstance(p[3], str)


def test_progression_index_with_element():
    elements = [MockElement(value=i) for i in range(5)]
    p = Progression(order=elements)
    assert p.index(elements[2]) == 2


def test_progression_index_with_start_end():
    p = Progression(order=[1, 2, 3, 2, 4])
    assert p.index(2, 2) == 3
    assert p.index(2, 0, 2) == 1

    with pytest.raises(ValueError):
        p.index(2, 4)  # 2 not found after index 4


def test_progression_count_with_element():
    elements = [MockElement(value=i) for i in range(3)] + [MockElement(value=1)]
    p = Progression(order=elements)
    assert p.count(elements[1]) == 2


@pytest.mark.parametrize("method", ["append", "include"])
def test_progression_append_include_equivalence(method):
    p1 = Progression()
    p2 = Progression()

    for i in range(5):
        getattr(p1, method)(i)
        getattr(p2, method)(str(i))

    assert p1 == p2


def test_progression_remove_all_occurrences():
    p = Progression(order=[1, 2, 3, 2, 4, 2])
    p.remove(2)
    assert list(p) == ["1", "3", "4"]


def test_progression_remove_with_element():
    elements = [MockElement(value=i) for i in range(5)]
    p = Progression(order=elements)
    p.remove(elements[2])
    assert len(p) == 4
    assert elements[2].ln_id not in p


def test_progression_extend_empty():
    p1 = Progression(order=[1, 2, 3])
    p2 = Progression()
    p1.extend(p2)
    assert list(p1) == ["1", "2", "3"]


def test_progression_extend_self():
    p = Progression(order=[1, 2, 3])
    p.extend(p)
    assert list(p) == ["1", "2", "3", "1", "2", "3"]


def test_progression_insert_at_end():
    p = Progression(order=[1, 2, 3])
    p.insert(3, 4)
    assert list(p) == ["1", "2", "3", "4"]


def test_progression_insert_out_of_range():
    p = Progression(order=[1, 2, 3])
    p.insert(10, 4)  # Should insert at the end
    assert list(p) == ["1", "2", "3", "4"]


def test_progression_insert_negative_index():
    p = Progression(order=[1, 2, 3])
    with pytest.raises(ValueError):
        p.insert(-1, 0)


@pytest.mark.parametrize(
    "slice_obj",
    [
        slice(None, None, 2),  # Every other element
        slice(1, None, None),  # From second element to end
        slice(None, -1, None),  # All but last element
        slice(None, None, -1),  # Reverse order
    ],
)
def test_progression_getitem_advanced_slicing(slice_obj):
    p = Progression(order=range(10))
    sliced = p[slice_obj]
    assert isinstance(sliced, Progression)
    assert list(sliced) == [str(i) for i in range(10)[slice_obj]]


def test_progression_setitem_with_progression():
    p1 = Progression(order=[1, 2, 3, 4, 5])
    p2 = Progression(order=[6, 7])
    p1[1:3] = p2
    assert list(p1) == ["1", "6", "7", "4", "5"]


def test_progression_delitem_advanced_slicing():
    p = Progression(order=range(10))
    del p[::2]  # Delete every other element
    assert list(p) == ["1", "3", "5", "7", "9"]


def test_progression_large_scale_operations():
    # Create a large progression
    large_p = Progression(order=range(100000))

    # Test various operations on the large progression
    assert len(large_p) == 100000
    assert large_p[50000] == "50000"
    large_p.append(100000)
    assert len(large_p) == 100001
    large_p.extend(Progression(order=range(100001, 110000)))
    assert len(large_p) == 110000
    del large_p[50000:60000]
    assert len(large_p) == 100000
    assert large_p[50000] == "60000"


def test_progression_thread_safety():
    import threading

    p = Progression()

    def worker(start, end):
        for i in range(start, end):
            p.append(i)
            p.remove(i)
            p.append(i)

    threads = [
        threading.Thread(target=worker, args=(i * 1000, (i + 1) * 1000))
        for i in range(10)
    ]

    for thread in threads:
        thread.start()

    for thread in threads:
        thread.join()

    assert len(p) == 10000
    assert set(p) == set(map(str, range(10000)))


def test_progression_memory_efficiency():
    import sys

    # Create a progression with a large number of elements
    p = Progression(order=range(1000000))

    # Calculate memory usage
    memory_usage = sys.getsizeof(p) + sum(sys.getsizeof(item) for item in p.order)

    # Check if memory usage is reasonable (less than 100MB for 1 million elements)
    assert memory_usage < 100 * 1024 * 1024  # 100MB in bytes


def test_progression_with_custom_id_elements():
    class CustomIdElement:
        def __init__(self, id_):
            self.id = id_

        def __eq__(self, other):
            return isinstance(other, CustomIdElement) and self.id == other.id

    elements = [CustomIdElement(str(i)) for i in range(5)]
    p = Progression(order=elements)

    assert len(p) == 5
    assert CustomIdElement("2") in p
    assert p.index(CustomIdElement("3")) == 3


def test_progression_exception_handling_advanced():
    p = Progression(order=[1, 2, 3])

    with pytest.raises(TypeError):
        p[1.5]  # Non-integer index

    with pytest.raises(ValueError):
        p.remove(MockElement(value=4))  # Element not in progression

    with pytest.raises(TypeError):
        p.extend([1, 2, 3])  # Extending with non-Progression


def test_progression_performance_comparison():
    import time

    # Create a large list and a large Progression
    large_list = list(range(1000000))
    large_prog = Progression(order=range(1000000))

    # Compare access time
    list_start = time.time()
    _ = large_list[500000]
    list_time = time.time() - list_start

    prog_start = time.time()
    _ = large_prog[500000]
    prog_time = time.time() - prog_start

    # Progression access should not be significantly slower than list access
    assert prog_time < list_time * 2


def test_progression_serialization_advanced():
    import json

    class ComplexElement(Element):
        data: dict

    p = Progression(
        order=[
            ComplexElement(data={"value": i, "nested": {"x": i * 2}}) for i in range(5)
        ]
    )

    serialized = json.dumps(p.to_dict())
    deserialized = Progression.from_dict(json.loads(serialized))

    assert len(deserialized) == 5
    assert all(isinstance(elem, str) for elem in deserialized)  # IDs are strings
    assert p == deserialized


# File: tests/test_progression.py
