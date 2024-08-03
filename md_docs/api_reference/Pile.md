# Pile Class Documentation

## Overview

The `Pile` class is a core container in the Lion framework, designed to store and manage collections of `Element` objects. It provides a flexible, ordered collection with both list-like and dictionary-like access patterns. The `Pile` class maintains the order of items while allowing fast access by unique identifiers.

## Class Definition

```python
class Pile(Element, Collective, Generic[T]):
    ...
```

The `Pile` class inherits from `Element` and `Collective`, and uses Generic typing for flexibility.

## Key Features

1. Ordered storage of `Element` objects
2. Both list-like and dictionary-like access patterns
3. Type checking for item inclusion
4. Arithmetic operations for combining Piles
5. Flexible item retrieval and manipulation methods

## Attributes

- `pile_` (dict[str, T]): Internal storage mapping identifiers to items.
- `item_type` (set[Type[Observable]] | None): Set of allowed item types.
- `order` (Progression): Progression specifying the order of item identifiers.
- `strict` (bool): Flag to enforce strict type checking if `item_type` is defined.

## Constructor

```python
def __init__(
    self,
    items: Any = None,
    item_type: set[Type[Observable]] | None = None,
    order: Progression | list | None = None,
    strict: bool = False,
):
    ...
```

Initializes a new Pile instance.

- `items`: Initial items for the pile.
- `item_type`: Allowed types for items in the pile.
- `order`: Initial order of items (as Progression).
- `strict`: Whether to enforce strict type checking.

## Methods

### Access and Retrieval

#### \__getitem__(key) -> T | Pile

Retrieve items from the pile using a key.

```python
from lion_core.generic import Pile as pile

p = pile([Node(value=i) for i in range(5)])
print(p[0])  # Output: Node with value 0
print(p[1:3])  # Output: Pile containing Nodes with values 1 and 2
```

#### \__setitem__(key, item) -> None

Set new values in the pile using various key types.

```python
p = pile([Node(value=i) for i in range(3)])
p[1] = Node(value=10)
print(p[1])
```

#### \__contains__(item: Any) -> bool

Check if item(s) are present in the pile.

```python
p = pile([Node(value=i) for i in range(3)])
print(Node(value=1) in p)  # Output: True
print(Node(value=5) in p)  # Output: False
```

#### get(key: Any, default=LN_UNDEFINED) -> T | Pile | None

Retrieve item(s) associated with given key.

```python
p = pile([Node(value=i) for i in range(3)])
print(p.get(1))  # Output: Node with value 1
print(p.get(5, "Not found"))  # Output: "Not found"
```

### Manipulation

#### pop(key: Any, default=LN_UNDEFINED) -> T | Pile | None

Remove and return item(s) associated with given key.

```python
p = pile([Node(value=i) for i in range(3)])
popped = p.pop(1)
print(popped)  # Output: Node with value 1
print(len(p))  # Output: 2
```

#### remove(item: T) -> None

Remove an item from the pile.

```python
p = pile([Node(value=i) for i in range(3)])
p.remove(Node(value=1))
print(len(p))  # Output: 2
```

#### include(item: Any)

Include item(s) in pile if not already present.

```python
p = pile([Node(value=i) for i in range(2)])
p.include(Node(value=2))
print(len(p))  # Output: 3
```

#### exclude(item: Any)

Exclude item(s) from pile if present.

```python
p = pile([Node(value=i) for i in range(3)])
p.exclude(Node(value=1))
print(len(p))  # Output: 2
```

#### clear() -> None

Remove all items from the pile.

```python
p = pile([Node(value=i) for i in range(3)])
p.clear()
print(len(p))  # Output: 0
```

#### update(other: Any)

Update pile with another collection of items.

```python
p1 = pile([Node(value=i) for i in range(2)])
p2 = pile([Node(value=i) for i in range(2, 4)])
p1.update(p2)
print(len(p1))  # Output: 4
```

#### append(item: T)

Append item to end of pile.

```python
p = pile([Node(value=i) for i in range(2)])
p.append(Node(value=2))
print(len(p))  # Output: 3
```

#### insert(index, item)

Insert item(s) at specific position.

```python
p = pile([Node(value=i) for i in range(2)])
p.insert(1, Node(value=10))
print(p[1])  # Output: Node with value 10
```

### Information

#### __len__() -> int

Get the number of items in the pile.

```python
p = pile([Node(value=i) for i in range(3)])
print(len(p))  # Output: 3
```

#### is_empty() -> bool

Check if the pile is empty.

```python
p = pile()
print(p.is_empty())  # Output: True
```

#### size() -> int

Get the number of items in the pile.

```python
p = pile([Node(value=i) for i in range(3)])
print(p.size())  # Output: 3
```

### Iteration

#### \__iter__() -> Iterable

Return an iterator over the items in the pile.

```python
p = pile([Node(value=i) for i in range(3)])
for node in p:
    print(node.value)  # Output: 0, 1, 2
```

#### keys() -> list

Get the keys of the pile in their specified order.

```python
p = pile([Node(value=i) for i in range(3)])
print(p.keys())  # Output: [ln_..., ln_..., ln_...]
```

#### values() -> list

Get the values of the pile in their specified order.

```python
p = pile([Node(value=i) for i in range(3)])
values = p.values()
print([node.value for node in values])  # Output: [0, 1, 2]
```

#### items() -> list[tuple[str, T]]

Get the items of the pile as (key, value) pairs in their order.

```python
p = pile([Node(value=i) for i in range(2)])
for key, node in p.items():
    print(f"{key}: {node.value}")  # Output: ln_...: 0, ln_...: 1
```

### Arithmetic Operations

#### \__add__(other: T) -> Pile

Create a new pile by including item(s) using `+`.

```python
p1 = pile([Node(value=i) for i in range(2)])
p2 = pile([Node(value=i) for i in range(2, 4)])
combined = p1 + p2
print(len(combined))  # Output: 4
```

#### \__sub__(other) -> Pile

Create a new pile by excluding item(s) using `-`.

```python
p = pile([Node(value=i) for i in range(3)])
result = p - Node(value=1)
print(len(result))  # Output: 2
```

#### \__iadd__(other: T) -> Pile

Include item(s) in the current pile in place using `+=`.

```python
p = pile([Node(value=i) for i in range(2)])
p += Node(value=2)
print(len(p))  # Output: 3
```

#### \__isub__(other) -> Pile

Exclude item(s) from the current pile in place using `-=`.

```python
p = pile([Node(value=i) for i in range(3)])
p -= Node(value=1)
print(len(p))  # Output: 2
```

## Usage Notes

1. The `Pile` class operates on Lion IDs internally, not on the actual `Element` objects.
2. Type checking is performed when adding items to ensure consistency within the `Pile`.
3. The `strict` flag determines whether subclasses of specified `item_type` are allowed.
4. Arithmetic operations (`+`, `-`, `+=`, `-=`) provide convenient ways to combine or modify `Pile` instances.
5. The `order` attribute (of type `Progression`) maintains the sequence of items, allowing for ordered operations.

## Example Usage

```python
from lion_core.generic import Node, Pile as pile

# Create a new Pile
p = pile([Node(value=i) for i in range(3)], name="TestPile")

# Add a new item
p.append(Node(value=3))

# Access items
print(p[0])  # Output: Node with value 0
print(p[1:3])  # Output: Pile containing Nodes with values 1 and 2

# Check if an item exists
print(Node(value=2) in p)  # Output: True

# Remove an item
p.remove(Node(value=1))

# Combine Piles
p2 = pile([Node(value=i) for i in range(4, 6)])
combined = p + p2

print(len(combined))  # Output: 5
```

## Conclusion

The `Pile` class is a versatile and powerful container in the Lion framework. Its combination of ordered storage, flexible access patterns, and type safety makes it suitable for a wide range of use cases within the framework. By understanding its capabilities and usage patterns, developers can effectively leverage the `Pile` class in their Lion framework projects.