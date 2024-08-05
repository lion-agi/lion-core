import pytest
from typing import Any, List
import asyncio
import random
import string
import sys
import time
from concurrent.futures import ThreadPoolExecutor

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
        {"key1": MockElement(value=1), "key2": MockElement(value=2)},
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


def test_getitem(sample_pile, sample_elements):
    assert sample_pile[0] == sample_elements[0]
    assert sample_pile[1:3] == Pile(items=sample_elements[1:3])
    assert sample_pile[sample_elements[2].ln_id] == sample_elements[2]


def test_getitem_invalid():
    p = Pile(items=[MockElement(value=i) for i in range(3)])
    with pytest.raises(ItemNotFoundError):
        p[10]
    with pytest.raises(ItemNotFoundError):
        p["nonexistent_id"]


def test_setitem(sample_pile):
    new_element = MockElement(value="new")
    sample_pile[0] = new_element
    assert sample_pile[0] == new_element

    new_elements = [MockElement(value="new1"), MockElement(value="new2")]
    sample_pile[1:3] = new_elements
    assert sample_pile[1:3] == Pile(items=new_elements)


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


def test_include(sample_pile, sample_elements):
    new_element = MockElement(value="new")
    sample_pile.include(new_element)
    assert new_element in sample_pile
    assert len(sample_pile) == 6

    with pytest.raises(ItemExistsError):
        sample_pile.include(sample_elements[0])


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


def test_performance_comparison():
    n = 100000
    elements = [MockElement(value=i) for i in range(n)]

    # Measure time for Pile operations
    start_time = time.time()
    p = Pile(items=elements)
    for i in range(1000):
        _ = p[random.randint(0, n - 1)]
    pile_time = time.time() - start_time

    # Measure time for dict operations
    start_time = time.time()
    d = {e.ln_id: e for e in elements}
    for i in range(1000):
        _ = d[elements[random.randint(0, n - 1)].ln_id]
    dict_time = time.time() - start_time

    # Pile should not be significantly slower than dict
    assert pile_time < dict_time * 2


def test_pile_with_custom_progression():
    custom_prog = Progression(order=[1, 2, 3, 4, 5])
    p = Pile(items=[MockElement(value=i) for i in range(5)], order=custom_prog)
    assert p.order == custom_prog


def test_pile_with_invalid_order():
    elements = [MockElement(value=i) for i in range(5)]
    with pytest.raises(LionValueError):
        Pile(items=elements, order=[1, 2, 3])  # Order length doesn't match items


def test_pile_serialization():
    elements = [MockElement(value=i) for i in range(5)]
    p = Pile(items=elements)
    serialized = p.to_dict()
    deserialized = Pile.from_dict(serialized)
    assert p == deserialized


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


def test_pile_thread_safety():
    p = Pile()

    def worker(start, end):
        for i in range(start, end):
            elem = MockElement(value=i)
            p.include(elem)
            p.exclude(elem)
            p.include(elem)

    with ThreadPoolExecutor(max_workers=10) as executor:
        futures = [executor.submit(worker, i * 1000, (i + 1) * 1000) for i in range(10)]
        for future in futures:
            future.result()

    assert len(p) == 10000
    assert set(e.value for e in p.values()) == set(range(10000))


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


def test_pile_with_different_id_types():
    class CustomIdElement:
        def __init__(self, id_):
            self.id = id_

    elements = [MockElement(value=1), CustomIdElement(id_="custom"), 2, "string_id"]
    p = Pile(items=elements)
    assert len(p) == 4
    assert all(item in p for item in elements)


def test_pile_exception_handling():
    p = Pile(items=[MockElement(value=i) for i in range(5)])

    with pytest.raises(LionTypeError):
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
    class CustomHashElement(Element):
        def __hash__(self):
            return hash(self.ln_id + str(self.value))

    elements = [CustomHashElement(value=i) for i in range(5)]
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
        elem = MockElement(value=i)
        p.include(elem)
        refs.append(weakref.ref(elem))

    del p
    gc.collect()

    # Check if all elements have been properly garbage collected
    assert sum(ref() is not None for ref in refs) == 0


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


def test_pile_custom_serialization():
    class SerializableElement(Element):
        def to_json(self):
            return json.dumps({"ln_id": self.ln_id, "value": self.value})

        @classmethod
        def from_json(cls, json_str):
            data = json.loads(json_str)
            return cls(ln_id=data["ln_id"], value=data["value"])

    elements = [SerializableElement(value=i) for i in range(5)]
    p = Pile(items=elements)

    serialized = json.dumps([e.to_json() for e in p.values()])
    deserialized = Pile(
        items=[SerializableElement.from_json(e) for e in json.loads(serialized)]
    )

    assert p == deserialized


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


def test_pile_with_inheritance():
    class SubPile(Pile):
        def custom_method(self):
            return sum(e.value for e in self.values())

    sp = SubPile(items=[MockElement(value=i) for i in range(5)])
    assert sp.custom_method() == 10


@pytest.mark.parametrize("operation", ["include", "exclude", "pop"])
def test_pile_operation_hooks(operation):
    class HookedPile(Pile):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            self.hook_called = False

        def _after_operation(self, operation: str, item: Any):
            self.hook_called = True

    hp = HookedPile()
    getattr(hp, operation)(MockElement(value=0))
    assert hp.hook_called


def test_pile_lazy_loading():
    class LazyElement(Element):
        def __init__(self, value):
            super().__init__()
            self._value = value
            self.loaded = False

        @property
        def value(self):
            if not self.loaded:
                # Simulate expensive loading operation
                import time

                time.sleep(0.1)
                self.loaded = True
            return self._value

    p = Pile(items=[LazyElement(i) for i in range(100)])

    # Accessing should trigger lazy loading
    assert p[50].value == 50
    assert p[50].loaded
    assert not p[51].loaded


def test_pile_with_property_access():
    class PropertyElement(Element):
        @property
        def squared(self):
            return self.value**2

    p = Pile(items=[PropertyElement(value=i) for i in range(10)])
    assert [e.squared for e in p.values()] == [i**2 for i in range(10)]


def test_pile_with_method_chaining():
    p = (
        Pile()
        .include(MockElement(value=1))
        .include(MockElement(value=2))
        .exclude(lambda x: x.value == 1)
        .include(MockElement(value=3))
    )

    assert len(p) == 2
    assert [e.value for e in p.values()] == [2, 3]


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


@pytest.mark.parametrize("chunk_size", [1, 2, 5])
def test_pile_chunking(chunk_size):
    p = Pile(items=[MockElement(value=i) for i in range(10)])
    chunks = list(p.chunks(chunk_size))
    assert len(chunks) == (10 + chunk_size - 1) // chunk_size
    assert all(isinstance(chunk, Pile) for chunk in chunks)
    assert sum(len(chunk) for chunk in chunks) == 10


def test_pile_filtering():
    p = Pile(items=[MockElement(value=i) for i in range(10)])
    filtered = p.filter(lambda x: x.value % 2 == 0)
    assert isinstance(filtered, Pile)
    assert len(filtered) == 5
    assert all(e.value % 2 == 0 for e in filtered.values())


def test_pile_mapping():
    p = Pile(items=[MockElement(value=i) for i in range(5)])
    mapped = p.map(lambda x: x.value * 2)
    assert isinstance(mapped, Pile)
    assert [e.value for e in mapped.values()] == [0, 2, 4, 6, 8]


def test_pile_reducing():
    p = Pile(items=[MockElement(value=i) for i in range(5)])
    result = p.reduce(lambda acc, x: acc + x.value, initial=0)
    assert result == 10


@pytest.mark.parametrize("n", [10, 100, 1000])
def test_pile_memory_usage(n):
    import sys

    p = Pile(items=[MockElement(value=i) for i in range(n)])
    memory_usage = sys.getsizeof(p) + sum(sys.getsizeof(e) for e in p.values())

    # Rough estimation: each MockElement should take about 100 bytes
    expected_usage = sys.getsizeof(p) + n * 100
    assert memory_usage < expected_usage * 1.2  # Allow 20% margin


def test_pile_with_metaclass():
    class PileMetaclass(type):
        def __new__(cls, name, bases, dct):
            dct["metaclass_attribute"] = "added by metaclass"
            return super().__new__(cls, name, bases, dct)

    class MetaPile(Pile, metaclass=PileMetaclass):
        pass

    mp = MetaPile()
    assert hasattr(mp, "metaclass_attribute")
    assert mp.metaclass_attribute == "added by metaclass"


def test_pile_with_slots():
    class SlottedElement(Element):
        __slots__ = ("value",)

        def __init__(self, value):
            super().__init__()
            self.value = value

    p = Pile(items=[SlottedElement(i) for i in range(100)])
    assert len(p) == 100
    assert not hasattr(p[0], "__dict__")


def test_pile_with_weakref():
    class WeakRefElement(Element):
        pass

    p = Pile()
    e = WeakRefElement()
    weak_e = weakref.ref(e)
    p.include(e)

    del e
    gc.collect()

    assert weak_e() is None
    assert len(p) == 1  # The pile still holds a reference


def test_pile_thread_local_storage():
    import threading

    class ThreadLocalPile(Pile):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            self.local = threading.local()

        def get_thread_id(self):
            if not hasattr(self.local, "thread_id"):
                self.local.thread_id = threading.get_ident()
            return self.local.thread_id

    tlp = ThreadLocalPile()

    def worker():
        assert tlp.get_thread_id() == threading.get_ident()

    threads = [threading.Thread(target=worker) for _ in range(5)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()


@pytest.mark.parametrize("size", [10, 100, 1000])
def test_pile_multiprocessing(size):
    def worker(pile_dict):
        p = Pile.from_dict(pile_dict)
        return sum(e.value for e in p.values())

    original_pile = Pile(items=[MockElement(value=i) for i in range(size)])
    pile_dict = original_pile.to_dict()

    with ProcessPoolExecutor() as executor:
        future = executor.submit(worker, pile_dict)
        result = future.result()

    assert result == sum(range(size))


def test_pile_with_descriptors():
    class DescriptorElement(Element):
        def __init__(self, value):
            super().__init__()
            self._value = value

        @property
        def value(self):
            return self._value

        @value.setter
        def value(self, new_value):
            if new_value < 0:
                raise ValueError("Value must be non-negative")
            self._value = new_value

    p = Pile(items=[DescriptorElement(i) for i in range(5)])

    with pytest.raises(ValueError):
        p[0].value = -1

    p[1].value = 10
    assert p[1].value == 10


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


def test_pile_with_dataclass():
    from dataclasses import dataclass

    @dataclass
    class DataClassElement(Element):
        value: int

    p = Pile(items=[DataClassElement(value=i) for i in range(5)])
    assert [e.value for e in p.values()] == list(range(5))


# File: tests/test_pile.py
