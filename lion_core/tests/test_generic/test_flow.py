import pytest
from typing import Any, List
import asyncio
import random
import string
import copy
from concurrent.futures import ThreadPoolExecutor

from lion_core.generic.flow import Flow
from lion_core.generic.progression import Progression, prog
from lion_core.generic.pile import Pile
from lion_core.generic.element import Element
from lion_core.generic.note import Note
from lion_core.exceptions import ItemNotFoundError, LionTypeError, LionValueError


class MockElement(Element):
    value: Any


@pytest.fixture
def sample_progressions():
    return [
        prog([MockElement(value=i) for i in range(3)], name=f"prog_{j}")
        for j in range(3)
    ]


@pytest.fixture
def sample_flow(sample_progressions):
    return Flow(progressions=sample_progressions, default_name="main")


def test_flow_initialization(sample_progressions):
    flow = Flow(progressions=sample_progressions)
    assert len(flow) == 3
    assert isinstance(flow.progressions, Pile)
    assert isinstance(flow.registry, Note)
    assert flow.default_name == "main"


def test_flow_initialization_with_custom_default():
    flow = Flow(default_name="custom_main")
    assert flow.default_name == "custom_main"


def test_flow_get_default_progression(sample_flow):
    default_prog = sample_flow.get()
    assert default_prog.name == "main"


def test_flow_get_specific_progression(sample_flow):
    prog = sample_flow.get("prog_1")
    assert prog.name == "prog_1"


def test_flow_get_nonexistent_progression(sample_flow):
    with pytest.raises(ItemNotFoundError):
        sample_flow.get("nonexistent")


def test_flow_getitem(sample_flow):
    assert sample_flow["prog_0"].name == "prog_0"
    with pytest.raises(ItemNotFoundError):
        sample_flow["nonexistent"]


def test_flow_setitem(sample_flow):
    new_prog = prog([MockElement(value=i) for i in range(5)], name="new_prog")
    sample_flow["new_prog"] = new_prog
    assert "new_prog" in sample_flow.registry
    assert len(sample_flow) == 4


def test_flow_size(sample_flow):
    assert sample_flow.size() == 9  # 3 progressions with 3 elements each


def test_flow_clear(sample_flow):
    sample_flow.clear()
    assert len(sample_flow) == 0
    assert len(sample_flow.registry) == 0


def test_flow_append(sample_flow):
    sample_flow.append(MockElement(value=10))
    assert sample_flow.get().size() == 4  # Appended to default progression


def test_flow_append_to_specific_progression(sample_flow):
    sample_flow.append(MockElement(value=10), "prog_1")
    assert sample_flow["prog_1"].size() == 4


def test_flow_include_item(sample_flow):
    new_element = MockElement(value=20)
    sample_flow.include(new_element)
    assert new_element in sample_flow.get()


def test_flow_include_progression(sample_flow):
    new_prog = prog([MockElement(value=i) for i in range(2)], name="new_prog")
    sample_flow.include(prog=new_prog)
    assert "new_prog" in sample_flow.registry
    assert len(sample_flow) == 4


def test_flow_exclude_item(sample_flow):
    element_to_exclude = sample_flow["prog_0"][0]
    sample_flow.exclude(element_to_exclude)
    assert element_to_exclude not in sample_flow["prog_0"]


def test_flow_exclude_item_from_all(sample_flow):
    element_to_exclude = MockElement(value=1)
    sample_flow.exclude(element_to_exclude, how="all")
    assert all(element_to_exclude not in p for p in sample_flow.progressions)


def test_flow_exclude_progression(sample_flow):
    sample_flow.exclude(prog="prog_1")
    assert "prog_1" not in sample_flow.registry
    assert len(sample_flow) == 2


def test_flow_remove(sample_flow):
    element_to_remove = sample_flow["prog_2"][1]
    sample_flow.remove(element_to_remove, "prog_2")
    assert element_to_remove not in sample_flow["prog_2"]


def test_flow_iteration(sample_flow):
    assert len(list(sample_flow)) == 3


def test_flow_keys_values_items(sample_flow):
    assert set(sample_flow.keys()) == {"prog_0", "prog_1", "prog_2"}
    assert len(list(sample_flow.values())) == 3
    assert len(list(sample_flow.items())) == 3


def test_flow_with_custom_progression_class():
    class CustomProgression(Progression):
        def custom_method(self):
            return sum(e.value for e in self)

    custom_prog = CustomProgression(
        order=[MockElement(value=i) for i in range(5)], name="custom"
    )
    custom_flow = Flow([custom_prog])
    assert custom_flow["custom"].custom_method() == 10


@pytest.mark.asyncio
async def test_flow_async_operations():
    async def async_append(flow, prog_name, value):
        await asyncio.sleep(0.1)
        flow.append(MockElement(value=value), prog_name)

    flow = Flow([prog(name="async_prog")])
    await asyncio.gather(*[async_append(flow, "async_prog", i) for i in range(5)])
    assert flow["async_prog"].size() == 5


def test_flow_large_scale():
    large_flow = Flow(
        [
            prog([MockElement(value=i) for i in range(1000)], name=f"large_prog_{j}")
            for j in range(10)
        ]
    )
    assert large_flow.size() == 10000
    assert len(large_flow) == 10


def test_flow_memory_usage():
    import sys

    small_flow = Flow([prog([MockElement(value=i) for i in range(10)], name="small")])
    large_flow = Flow([prog([MockElement(value=i) for i in range(1000)], name="large")])

    small_size = sys.getsizeof(small_flow) + sum(
        sys.getsizeof(p) for p in small_flow.progressions
    )
    large_size = sys.getsizeof(large_flow) + sum(
        sys.getsizeof(p) for p in large_flow.progressions
    )

    # Ensure memory usage scales reasonably
    assert large_size < small_size * 150  # Adjust as needed


def test_flow_deep_copy():
    original_flow = Flow([prog([MockElement(value=i) for i in range(3)], name="orig")])
    copied_flow = copy.deepcopy(original_flow)

    assert original_flow == copied_flow
    assert original_flow is not copied_flow
    assert all(
        a is not b for a, b in zip(original_flow.progressions, copied_flow.progressions)
    )


def test_flow_with_generator_input():
    def prog_generator():
        for i in range(5):
            yield prog([MockElement(value=j) for j in range(i)], name=f"gen_prog_{i}")

    gen_flow = Flow(progressions=prog_generator())
    assert len(gen_flow) == 5
    assert gen_flow["gen_prog_4"].size() == 4


@pytest.mark.parametrize("n_progs, prog_size", [(10, 100), (100, 10), (1000, 1)])
def test_flow_performance_scaling(n_progs, prog_size):
    import time

    start_time = time.time()

    large_flow = Flow(
        [
            prog(
                [MockElement(value=i) for i in range(prog_size)], name=f"perf_prog_{j}"
            )
            for j in range(n_progs)
        ]
    )

    creation_time = time.time() - start_time

    start_time = time.time()
    for _ in range(100):
        random_prog = random.choice(list(large_flow.keys()))
        _ = large_flow[random_prog]

    access_time = time.time() - start_time

    assert creation_time < 1.0  # Adjust as needed
    assert access_time < 0.1  # Adjust as needed


def test_flow_thread_safety():
    shared_flow = Flow([prog(name="shared")])

    def worker(start, end):
        for i in range(start, end):
            shared_flow.append(MockElement(value=i), "shared")
            if i % 2 == 0:
                shared_flow.remove(MockElement(value=i - 1), "shared")

    with ThreadPoolExecutor(max_workers=4) as executor:
        futures = [executor.submit(worker, i * 250, (i + 1) * 250) for i in range(4)]
        for future in futures:
            future.result()

    assert (
        450 <= shared_flow["shared"].size() <= 550
    )  # Allow for some variance due to threading


def test_flow_error_handling():
    error_flow = Flow()

    with pytest.raises(LionTypeError):
        error_flow.include(42)  # Invalid type for inclusion

    with pytest.raises(ItemNotFoundError):
        error_flow.exclude(prog="nonexistent")

    with pytest.raises(LionValueError):
        Flow(progressions=42)  # Invalid input for initialization


def test_flow_with_custom_pile():
    class CustomPile(Pile):
        def custom_method(self):
            return len(self)

    custom_flow = Flow()
    custom_flow.progressions = CustomPile()
    custom_flow.include(prog([MockElement(value=i) for i in range(5)], name="custom"))

    assert custom_flow.progressions.custom_method() == 1


def test_flow_serialization():
    original_flow = Flow(
        [
            prog([MockElement(value=i) for i in range(3)], name=f"ser_prog_{j}")
            for j in range(3)
        ]
    )
    serialized = original_flow.to_dict()
    deserialized = Flow.from_dict(serialized)

    assert len(original_flow) == len(deserialized)
    assert all(
        op.name == dp.name
        for op, dp in zip(original_flow.progressions, deserialized.progressions)
    )
    assert all(
        op.size() == dp.size()
        for op, dp in zip(original_flow.progressions, deserialized.progressions)
    )


def test_flow_with_nested_flows():
    nested_flow = Flow(
        [
            prog([MockElement(value=i) for i in range(3)], name="outer"),
            Flow([prog([MockElement(value=i) for i in range(2)], name="inner")]),
        ]
    )

    assert len(nested_flow) == 2
    assert isinstance(nested_flow.progressions[1], Flow)
    assert nested_flow.progressions[1]["inner"].size() == 2


def test_flow_with_dynamic_progression_addition():
    dynamic_flow = Flow()
    for i in range(5):
        dynamic_flow.include(
            prog([MockElement(value=j) for j in range(i)], name=f"dynamic_{i}")
        )

    assert len(dynamic_flow) == 5
    assert dynamic_flow["dynamic_4"].size() == 4


def test_flow_with_progression_reordering():
    reorder_flow = Flow([prog(name=f"reorder_{i}") for i in range(5)])
    original_order = list(reorder_flow.keys())

    # Simulate reordering
    reordered = original_order[2:] + original_order[:2]
    reorder_flow.progressions = Pile(
        [reorder_flow.progressions[name] for name in reordered]
    )

    assert list(reorder_flow.keys()) == reordered


def test_flow_with_progression_filtering():
    filter_flow = Flow(
        [
            prog([MockElement(value=i) for i in range(j)], name=f"filter_{j}")
            for j in range(5)
        ]
    )

    # Filter progressions with more than 2 elements
    filtered = Flow([p for p in filter_flow.progressions if p.size() > 2])

    assert len(filtered) == 2
    assert all(p.size() > 2 for p in filtered.progressions)


@pytest.mark.parametrize("op", ["union", "intersection", "difference"])
def test_flow_set_operations(op):
    flow1 = Flow([prog([MockElement(value=i) for i in range(5)], name="set_op_1")])
    flow2 = Flow([prog([MockElement(value=i) for i in range(3, 8)], name="set_op_2")])

    if op == "union":
        result = Flow(
            [prog(set(flow1["set_op_1"]) | set(flow2["set_op_2"]), name="union")]
        )
        assert result["union"].size() == 8
    elif op == "intersection":
        result = Flow(
            [prog(set(flow1["set_op_1"]) & set(flow2["set_op_2"]), name="intersection")]
        )
        assert result["intersection"].size() == 2
    elif op == "difference":
        result = Flow(
            [prog(set(flow1["set_op_1"]) - set(flow2["set_op_2"]), name="difference")]
        )
        assert result["difference"].size() == 3


def test_flow_with_custom_element_types():
    class ComplexElement(Element):
        def __init__(self, real, imag):
            super().__init__()
            self.real = real
            self.imag = imag

    complex_flow = Flow(
        [prog([ComplexElement(i, i + 1) for i in range(5)], name="complex")]
    )
    assert complex_flow["complex"].size() == 5
    assert isinstance(complex_flow["complex"][0], ComplexElement)


def test_flow_progression_dependency():
    dep_flow = Flow(
        [
            prog([MockElement(value=i) for i in range(5)], name="source"),
            prog(name="dependent"),
        ]
    )

    # Simulate dependency: dependent progression gets squares of source values
    dep_flow["dependent"] = prog(
        [MockElement(value=e.value**2) for e in dep_flow["source"]], name="dependent"
    )

    assert dep_flow["dependent"].size() == 5
    assert [e.value for e in dep_flow["dependent"]] == [0, 1, 4, 9, 16]


def test_flow_progression_lazy_evaluation():
    class LazyProgression(Progression):
        def __init__(self, func, *args, **kwargs):
            super().__init__(*args, **kwargs)
            self.func = func
            self._evaluated = False

        def __iter__(self):
            if not self._evaluated:
                self.order = list(self.func())
                self._evaluated = True
            return super().__iter__()

    def lazy_range(n):
        return (MockElement(value=i) for i in range(n))

    lazy_flow = Flow([LazyProgression(lambda: lazy_range(1000000), name="lazy")])

    assert not lazy_flow["lazy"]._evaluated
    assert next(iter(lazy_flow["lazy"])).value == 0
    assert lazy_flow["lazy"]._evaluated


def test_flow_with_progression_composition():
    flow = Flow(
        [
            prog([MockElement(value=i) for i in range(5)], name="base"),
            prog(name="composed"),
        ]
    )

    flow["composed"] = prog(
        [
            MockElement(value=sum(e.value for e in flow["base"][: i + 1]))
            for i in range(flow["base"].size())
        ],
        name="composed",
    )

    assert [e.value for e in flow["composed"]] == [0, 1, 3, 6, 10]


def test_flow_with_progression_mapping():
    flow = Flow([prog([MockElement(value=i) for i in range(5)], name="original")])

    mapped_prog = prog(
        map(lambda e: MockElement(value=e.value * 2), flow["original"]), name="mapped"
    )
    flow.include(mapped_prog)

    assert [e.value for e in flow["mapped"]] == [0, 2, 4, 6, 8]


def test_flow_with_progression_filtering():
    flow = Flow([prog([MockElement(value=i) for i in range(10)], name="unfiltered")])

    filtered_prog = prog(
        filter(lambda e: e.value % 2 == 0, flow["unfiltered"]), name="filtered"
    )
    flow.include(filtered_prog)

    assert [e.value for e in flow["filtered"]] == [0, 2, 4, 6, 8]


def test_flow_with_progression_reduction():
    flow = Flow([prog([MockElement(value=i) for i in range(5)], name="reducible")])

    result = sum(e.value for e in flow["reducible"])

    assert result == 10


@pytest.mark.asyncio
async def test_flow_with_async_progression():
    class AsyncProgression(Progression):
        async def async_sum(self):
            return sum(e.value for e in self)

    async_flow = Flow(
        [AsyncProgression([MockElement(value=i) for i in range(5)], name="async")]
    )

    result = await async_flow["async"].async_sum()
    assert result == 10


def test_flow_with_progression_chaining():
    flow = Flow(
        [
            prog([MockElement(value=i) for i in range(10)], name="start"),
            prog(name="filtered"),
            prog(name="mapped"),
            prog(name="result"),
        ]
    )

    flow["filtered"] = prog(
        filter(lambda e: e.value % 2 == 0, flow["start"]), name="filtered"
    )
    flow["mapped"] = prog(
        map(lambda e: MockElement(value=e.value * 2), flow["filtered"]), name="mapped"
    )
    flow["result"] = prog(flow["mapped"], name="result")

    assert [e.value for e in flow["result"]] == [0, 4, 8, 12, 16]


def test_flow_with_circular_dependency_detection():
    flow = Flow([prog(name="a"), prog(name="b"), prog(name="c")])

    # Create a circular dependency
    flow["a"] = prog([MockElement(value=1)], name="a")
    flow["b"] = prog([e for e in flow["a"]], name="b")
    flow["c"] = prog([e for e in flow["b"]], name="c")

    with pytest.raises(ValueError):
        flow["a"] = prog([e for e in flow["c"]], name="a")


def test_flow_with_dynamic_progression_creation():
    def create_progression(n):
        return prog([MockElement(value=i**2) for i in range(n)], name=f"dynamic_{n}")

    dynamic_flow = Flow()
    for i in range(1, 6):
        dynamic_flow.include(create_progression(i))

    assert len(dynamic_flow) == 5
    assert [e.value for e in dynamic_flow["dynamic_5"]] == [0, 1, 4, 9, 16]


def test_flow_with_progression_sorting():
    flow = Flow(
        [prog([MockElement(value=i) for i in reversed(range(5))], name="unsorted")]
    )

    sorted_prog = prog(sorted(flow["unsorted"], key=lambda e: e.value), name="sorted")
    flow.include(sorted_prog)

    assert [e.value for e in flow["sorted"]] == [0, 1, 2, 3, 4]


def test_flow_with_progression_grouping():
    flow = Flow([prog([MockElement(value=i) for i in range(10)], name="ungrouped")])

    from itertools import groupby

    grouped = groupby(flow["ungrouped"], key=lambda e: e.value % 2)
    flow["grouped"] = prog(
        {k: prog(v, name=f"group_{k}") for k, v in grouped}, name="grouped"
    )

    assert len(flow["grouped"][0]) == 5
    assert len(flow["grouped"][1]) == 5


def test_flow_with_progression_zipping():
    flow = Flow(
        [
            prog([MockElement(value=i) for i in range(5)], name="a"),
            prog([MockElement(value=i * 2) for i in range(5)], name="b"),
        ]
    )

    zipped_prog = prog(zip(flow["a"], flow["b"]), name="zipped")
    flow.include(zipped_prog)

    assert [(a.value, b.value) for a, b in flow["zipped"]] == [
        (0, 0),
        (1, 2),
        (2, 4),
        (3, 6),
        (4, 8),
    ]


def test_flow_with_progression_flattening():
    nested_prog = prog(
        [
            prog([MockElement(value=i) for i in range(3)], name=f"nested_{j}")
            for j in range(3)
        ],
        name="nested",
    )

    flow = Flow([nested_prog])

    flattened_prog = prog((e for p in flow["nested"] for e in p), name="flattened")
    flow.include(flattened_prog)

    assert flow["flattened"].size() == 9
    assert [e.value for e in flow["flattened"]] == [0, 1, 2, 0, 1, 2, 0, 1, 2]


def test_flow_with_progression_windowing():
    from collections import deque

    flow = Flow([prog([MockElement(value=i) for i in range(10)], name="original")])

    def window(seq, n=2):
        it = iter(seq)
        win = deque((next(it, None) for _ in range(n)), maxlen=n)
        yield win
        append = win.append
        for e in it:
            append(e)
            yield win

    windowed_prog = prog(window(flow["original"], 3), name="windowed")
    flow.include(windowed_prog)

    assert flow["windowed"].size() == 8
    assert [[e.value for e in w] for w in flow["windowed"]] == [
        [0, 1, 2],
        [1, 2, 3],
        [2, 3, 4],
        [3, 4, 5],
        [4, 5, 6],
        [5, 6, 7],
        [6, 7, 8],
        [7, 8, 9],
    ]


def test_flow_with_progression_caching():
    class CachedProgression(Progression):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            self._cache = {}

        def get_or_compute(self, key, compute_func):
            if key not in self._cache:
                self._cache[key] = compute_func()
            return self._cache[key]

    flow = Flow(
        [CachedProgression([MockElement(value=i) for i in range(100)], name="cached")]
    )

    def expensive_computation(n):
        return sum(e.value for e in flow["cached"][:n])

    assert flow["cached"].get_or_compute(10, lambda: expensive_computation(10)) == 45
    assert (
        flow["cached"].get_or_compute(10, lambda: expensive_computation(10)) == 45
    )  # Should use cache


def test_flow_with_progression_pagination():
    flow = Flow([prog([MockElement(value=i) for i in range(100)], name="long")])

    def paginate(progression, page_size=10):
        for i in range(0, len(progression), page_size):
            yield prog(progression[i : i + page_size], name=f"page_{i//page_size}")

    paginated_flow = Flow(paginate(flow["long"]))

    assert len(paginated_flow) == 10
    assert all(p.size() == 10 for p in paginated_flow.progressions)
    assert [e.value for e in paginated_flow["page_5"]] == list(range(50, 60))


def test_flow_with_progression_versioning():
    class VersionedProgression(Progression):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            self.versions = [self.order.copy()]

        def update(self, new_order):
            self.order = new_order
            self.versions.append(self.order.copy())

        def rollback(self, version):
            if 0 <= version < len(self.versions):
                self.order = self.versions[version]
            else:
                raise ValueError("Invalid version number")

    flow = Flow(
        [
            VersionedProgression(
                [MockElement(value=i) for i in range(5)], name="versioned"
            )
        ]
    )

    flow["versioned"].update([MockElement(value=i * 2) for i in range(5)])
    flow["versioned"].update([MockElement(value=i**2) for i in range(5)])

    assert [e.value for e in flow["versioned"]] == [0, 1, 4, 9, 16]

    flow["versioned"].rollback(0)
    assert [e.value for e in flow["versioned"]] == [0, 1, 2, 3, 4]


def test_flow_with_progression_diff():
    flow = Flow(
        [
            prog([MockElement(value=i) for i in range(5)], name="original"),
            prog(
                [MockElement(value=i * 2) for i in range(3)]
                + [MockElement(value=i) for i in range(6, 8)],
                name="modified",
            ),
        ]
    )

    diff_prog = prog(
        [
            (i, (a.value if a else None), (b.value if b else None))
            for i, (a, b) in enumerate(zip(flow["original"], flow["modified"]))
            if (a and b and a.value != b.value) or (bool(a) != bool(b))
        ],
        name="diff",
    )

    flow.include(diff_prog)

    assert [(i, a, b) for i, a, b in flow["diff"]] == [
        (1, 1, 2),
        (2, 2, 4),
        (3, 3, 6),
        (4, 4, 7),
    ]


# File: tests/test_flow_extended.py
