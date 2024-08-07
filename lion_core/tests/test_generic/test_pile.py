import pytest
from typing import Any, List
import asyncio
import random
import string
import sys
import time
from concurrent.futures import ThreadPoolExecutor

from lion_core.generic.component import Component
from lion_core.generic.pile import Pile, pile
from lion_core.generic.element import Element
from lion_core.exceptions import (
    ItemNotFoundError,
    ItemExistsError,
    LionTypeError,
    LionValueError,
)
from lion_core.sys_utils import SysUtil
from lion_core.generic.progression import Progression


class MockElement(Element):
    value: Any


@pytest.fixture
def sample_elements():
    return [MockElement(value=i) for i in range(5)]


@pytest.fixture
def sample_pile(sample_elements):
    return Pile(items=sample_elements)


def generate_random_string(length: int) -> str:
    return "".join(random.choices(string.ascii_letters + string.digits, k=length))


@pytest.mark.parametrize(
    "input_data",
    [
        [],
        [MockElement(value=i) for i in range(3)],
    ],
)
def test_initialization(input_data):
    p = Pile(items=input_data)
    assert len(p) == len(input_data)
    for item in input_data:
        assert SysUtil.get_id(item) in p


def test_initialization_with_item_type():
    p = Pile(items=[MockElement(value=i) for i in range(3)], item_type=MockElement)
    assert p.item_type == {MockElement}

    with pytest.raises(LionTypeError):
        Pile(items=[1, 2, 3], item_type=MockElement)


def test_getitem_invalid():
    p = Pile(items=[MockElement(value=i) for i in range(3)])
    with pytest.raises(ItemNotFoundError):
        p[10]
    with pytest.raises(ItemNotFoundError):
        p["nonexistent_id"]


def test_contains(sample_pile, sample_elements):
    assert sample_elements[0] in sample_pile
    assert sample_elements[0].ln_id in sample_pile
    assert MockElement(value="nonexistent") not in sample_pile


def test_keys_values_items(sample_pile, sample_elements):
    assert list(sample_pile.keys()) == [e.ln_id for e in sample_elements]
    assert list(sample_pile.values()) == sample_elements
    assert list(sample_pile.items()) == [(e.ln_id, e) for e in sample_elements]


def test_get(sample_pile, sample_elements):
    assert sample_pile.get(0) == sample_elements[0]
    assert sample_pile.get(sample_elements[1].ln_id) == sample_elements[1]
    assert sample_pile.get("nonexistent", default="default") == "default"


def test_pop(sample_pile, sample_elements):
    popped = sample_pile.pop(1)
    assert popped == sample_elements[1]
    assert popped not in sample_pile
    assert len(sample_pile) == 4

    with pytest.raises(ItemNotFoundError):
        sample_pile.pop("nonexistent")


def test_remove(sample_pile, sample_elements):
    sample_pile.remove(sample_elements[2])
    assert sample_elements[2] not in sample_pile
    assert len(sample_pile) == 4

    with pytest.raises(ItemNotFoundError):
        sample_pile.remove(MockElement(value="nonexistent"))


def test_exclude(sample_pile, sample_elements):
    sample_pile.exclude(sample_elements[3])
    assert sample_elements[3] not in sample_pile
    assert len(sample_pile) == 4

    # Excluding non-existent item should not raise an error
    sample_pile.exclude(MockElement(value="nonexistent"))


def test_clear(sample_pile):
    sample_pile.clear()
    assert len(sample_pile) == 0


def test_update(sample_pile, sample_elements):
    new_elements = [MockElement(value="new1"), MockElement(value="new2")]
    sample_pile.update(new_elements)
    assert len(sample_pile) == 7
    assert all(e in sample_pile for e in new_elements)


def test_is_empty(sample_pile):
    assert not sample_pile.is_empty()
    sample_pile.clear()
    assert sample_pile.is_empty()


def test_size(sample_pile, sample_elements):
    assert sample_pile.size() == len(sample_elements)


def test_append(sample_pile, sample_elements):
    new_element = MockElement(value="new")
    sample_pile.append(new_element)
    assert new_element in sample_pile
    assert len(sample_pile) == 6


def test_insert(sample_pile, sample_elements):
    new_element = MockElement(value="new")
    sample_pile.insert(2, new_element)
    assert sample_pile[2] == new_element
    assert len(sample_pile) == 6


def test_add_sub_operations(sample_pile, sample_elements):
    new_element = MockElement(value="new")
    new_pile = sample_pile + new_element
    assert len(new_pile) == 6
    assert new_element in new_pile

    sub_pile = sample_pile - sample_elements[1]
    assert len(sub_pile) == 4
    assert sample_elements[1] not in sub_pile


def test_iadd_isub_operations(sample_pile, sample_elements):
    new_element = MockElement(value="new")
    sample_pile += new_element
    assert len(sample_pile) == 6
    assert new_element in sample_pile

    sample_pile -= sample_elements[1]
    assert len(sample_pile) == 5
    assert sample_elements[1] not in sample_pile


def test_iter(sample_pile, sample_elements):
    for item in sample_pile:
        assert item in sample_elements


def test_strict_mode():
    strict_pile = Pile(
        items=[MockElement(value=i) for i in range(3)],
        item_type=MockElement,
        strict=True,
    )
    with pytest.raises(LionTypeError):
        strict_pile.include(Element())  # Not a MockElement


def test_order_preservation():
    elements = [MockElement(value=i) for i in range(10)]
    p = Pile(items=elements)
    assert list(p.values()) == elements

    # Test order after operations
    p.remove(elements[5])
    p.include(MockElement(value="new"))
    assert list(p.values())[:5] == elements[:5]
    assert list(p.values())[5:9] == elements[6:]
    assert list(p.values())[9].value == "new"


@pytest.mark.asyncio
async def test_concurrent_operations():
    p = Pile()

    async def add_items():
        for _ in range(1000):
            p.include(MockElement(value=generate_random_string(10)))
            await asyncio.sleep(0.001)

    async def remove_items():
        for _ in range(500):
            if not p.is_empty():
                p.pop(0)
            await asyncio.sleep(0.002)

    await asyncio.gather(add_items(), remove_items())
    assert 450 <= len(p) <= 550  # Allow for some variance due to timing


def test_large_scale_operations():
    large_pile = Pile(items=[MockElement(value=i) for i in range(100000)])
    assert len(large_pile) == 100000

    # Test various operations on the large pile
    assert large_pile[50000].value == 50000
    large_pile.include(MockElement(value=100000))
    assert len(large_pile) == 100001
    large_pile.exclude(large_pile[50000])
    assert len(large_pile) == 100000
    assert large_pile[50000].value == 50001


def test_memory_efficiency():
    elements = [MockElement(value=i) for i in range(100000)]
    p = Pile(items=elements)

    # Calculate memory usage
    pile_size = sys.getsizeof(p)
    internal_size = sum(sys.getsizeof(item) for item in p.pile_.values())
    total_size = pile_size + internal_size

    # Check if memory usage is reasonable (less than 100MB for 100,000 elements)
    assert total_size < 100 * 1024 * 1024  # 100MB in bytes


def test_pile_with_custom_progression():
    custom_prog = Progression(order=[1, 2, 3, 4, 5])
    p = Pile(items=[MockElement(value=i) for i in range(5)], order=custom_prog)
    assert p.order == custom_prog


def test_pile_with_invalid_order():
    elements = [MockElement(value=i) for i in range(5)]
    with pytest.raises(LionValueError):
        Pile(items=elements, order=[1, 2, 3])  # Order length doesn't match items


def test_pile_with_complex_elements():
    class ComplexElement(Element):
        data: dict

    elements = [
        ComplexElement(data={"value": i, "nested": {"x": i * 2}}) for i in range(5)
    ]
    p = Pile(items=elements)
    assert len(p) == 5
    assert all(isinstance(e, ComplexElement) for e in p.values())
    assert p[2].data["nested"]["x"] == 4


def test_pile_with_generator_input():
    def element_generator():
        for i in range(1000):
            yield MockElement(value=i)

    p = Pile(items=element_generator())
    assert len(p) == 1000
    assert all(i == e.value for i, e in enumerate(p.values()))


@pytest.mark.asyncio
async def test_pile_with_async_generator_input():
    async def async_element_generator():
        for i in range(1000):
            await asyncio.sleep(0.001)
            yield MockElement(value=i)

    p = Pile(items=[e async for e in async_element_generator()])
    assert len(p) == 1000
    assert all(i == e.value for i, e in enumerate(p.values()))


def test_pile_exception_handling():
    p = Pile(items=[MockElement(value=i) for i in range(5)])

    with pytest.raises(ItemNotFoundError):
        p[1.5]  # Non-integer, non-string index

    with pytest.raises(ItemNotFoundError):
        p.remove(MockElement(value=10))  # Element not in pile

    with pytest.raises(LionValueError):
        p.update(5)  # Invalid update input


def test_pile_function():
    elements = [MockElement(value=i) for i in range(5)]
    p = pile(items=elements, item_type=MockElement)
    assert isinstance(p, Pile)
    assert len(p) == 5
    assert p.item_type == {MockElement}


import pytest
import random
import string
import json
import pickle
import copy
from typing import Any, List, Dict
import asyncio
from concurrent.futures import ProcessPoolExecutor
import multiprocessing
import gc
import weakref

from lion_core.generic.pile import Pile, pile
from lion_core.generic.element import Element
from lion_core.exceptions import (
    ItemNotFoundError,
    ItemExistsError,
    LionTypeError,
    LionValueError,
)
from lion_core.sys_utils import SysUtil
from lion_core.generic.progression import Progression


class ComplexElement(Element):
    data: Dict[str, Any]
    nested: List[Dict[str, Any]]


@pytest.fixture
def complex_elements():
    return [
        ComplexElement(
            data={"value": i, "name": f"Element{i}"},
            nested=[{"x": i * 2, "y": i * 3} for _ in range(3)],
        )
        for i in range(10)
    ]


def test_pile_with_complex_elements(complex_elements):
    p = Pile(items=complex_elements)
    assert len(p) == 10
    assert p[3].data["name"] == "Element3"
    assert p[5].nested[1]["y"] == 15


def test_pile_nested_operations():
    p = Pile(
        items=[Pile(items=[MockElement(value=i) for i in range(3)]) for _ in range(3)]
    )
    assert len(p) == 3
    assert all(isinstance(item, Pile) for item in p.values())
    assert len(p[0]) == 3


def test_pile_with_custom_hash_elements():
    class CustomHashElement(Component):
        def __hash__(self):
            return hash(self.ln_id + str(self.value))

    elements = [CustomHashElement(content=i) for i in range(5)]
    p = Pile(items=elements)
    assert len(p) == 5
    assert elements[2] in p


@pytest.mark.parametrize("n", [100, 1000, 10000])
def test_pile_scaling_performance(n):
    import time

    elements = [MockElement(value=i) for i in range(n)]

    start_time = time.time()
    p = Pile(items=elements)
    creation_time = time.time() - start_time

    start_time = time.time()
    for _ in range(100):
        _ = p[random.randint(0, n - 1)]
    access_time = time.time() - start_time

    # Asserting that creation and access times scale reasonably
    assert creation_time < 0.1 * n / 1000  # Adjust as needed
    assert access_time < 0.01 * n / 1000  # Adjust as needed


def test_pile_memory_leak():
    import gc
    import weakref

    p = Pile()
    refs = []

    for i in range(1000):
        elem = Component(content=i)
        p.include(elem)
        refs.append(weakref.ref(elem))

    del p
    gc.collect()

    # Check if all elements have been properly garbage collected
    assert sum(ref() is not None for ref in refs) == 1


@pytest.mark.asyncio
async def test_pile_async_iteration():
    p = Pile(items=[MockElement(value=i) for i in range(100)])

    async def async_sum():
        total = 0
        async for item in p:
            total += item.value
            await asyncio.sleep(0.01)
        return total

    result = await async_sum()
    assert result == sum(range(100))


def test_pile_pickling():
    p = Pile(items=[MockElement(value=i) for i in range(10)])
    pickled = pickle.dumps(p)
    unpickled = pickle.loads(pickled)
    assert p == unpickled


def test_pile_deep_copy():
    p = Pile(items=[MockElement(value=i) for i in range(10)])
    p_copy = copy.deepcopy(p)
    assert p == p_copy
    assert p is not p_copy
    assert all(a is not b for a, b in zip(p.values(), p_copy.values()))


def test_pile_with_property_access():
    class PropertyElement(Component):
        @property
        def squared(self):
            return self.content**2

    p = Pile(items=[PropertyElement(content=i) for i in range(10)])
    assert [e.squared for e in p.values()] == [i**2 for i in range(10)]


def test_pile_with_context_manager():
    class ManagedPile(Pile):
        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc_val, exc_tb):
            self.clear()

    with ManagedPile(items=[MockElement(value=i) for i in range(5)]) as mp:
        assert len(mp) == 5
    assert len(mp) == 0


def test_pile_with_custom_progression():
    class ReversedProgression(Progression):
        def __iter__(self):
            return reversed(self.order)

    elements = [MockElement(value=i) for i in range(5)]
    p = Pile(
        items=elements, order=ReversedProgression(order=[e.ln_id for e in elements])
    )
    assert [e.value for e in p.values()] == [4, 3, 2, 1, 0]


@pytest.mark.parametrize("n", [10, 100, 1000])
def test_pile_memory_usage(n):
    import sys

    p = Pile(items=[MockElement(value=i) for i in range(n)])
    memory_usage = sys.getsizeof(p) + sum(sys.getsizeof(e) for e in p.values())

    # Rough estimation: each MockElement should take about 100 bytes
    expected_usage = sys.getsizeof(p) + n * 100
    assert memory_usage < expected_usage * 1.2  # Allow 20% margin


def test_pile_with_weakref():
    class WeakRefElement(Element):
        pass

    p = Pile()
    refs = []
    for _ in range(10):
        e = WeakRefElement()
        weak_e = weakref.ref(e)
        refs.append(weak_e)
        p.include(e)

    del p
    gc.collect()

    assert sum(ref() is not None for ref in refs) == 1


def test_pile_with_abc():
    from abc import ABC, abstractmethod

    class AbstractElement(Element, ABC):
        @abstractmethod
        def abstract_method(self):
            pass

    class ConcreteElement(AbstractElement):
        def abstract_method(self):
            return "Implemented"

    p = Pile(items=[ConcreteElement() for _ in range(5)])
    assert all(e.abstract_method() == "Implemented" for e in p.values())

    with pytest.raises(TypeError):
        Pile(items=[AbstractElement()])


# File: tests/test_pile.py
