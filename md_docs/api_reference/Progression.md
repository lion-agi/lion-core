# Progression Class Documentation

## Overview

The `Progression` class is a core component of the Lion framework, designed to manage and manipulate ordered sequences of items using their Lion IDs. It combines list-like functionality with Lion-specific features, providing a powerful tool for handling collections within the framework.

## Class Definition

```python
class Progression(Element, Ordering):
    ...
```

## Key Features

1. Ordered management of Lion IDs
2. List-like indexing and Lion ID-based operations
3. Comprehensive item manipulation methods
4. Common sequence operations
5. Arithmetic operations for combining progressions

## Attributes

- `name` (str | None): Optional name for the progression.
- `order` (list[str]): Ordered list of Lion IDs.

## Methods

### Core Operations

#### \__init__(order: list[str] | None = None, name: str | None = None)

Initializes a new Progression instance.

```python
@field_validator("order", mode="before")
def _validate_order(cls, value):
    return validate_order(value)
```

This method ensures that the initial order is properly validated.

#### \__contains__(item: Any) -> bool

Checks if an item or items are in the progression.

```python
if item is None or not self.order:
    return False

item = to_list_type(item) if not isinstance(item, list) else item

check = False
for i in item:
    check = False
    if isinstance(i, str):
        check = i in self.order
    elif isinstance(i, Element):
        check = i.ln_id in self.order
    if not check:
        return False

return check
```

#### \__getitem__(key: int | slice) -> str | Progression

Retrieves an item or slice of items from the progression.

```python
try:
    a = self.order[key]
    if not a:
        raise ItemNotFoundError(f"index {key} item not found")
    if isinstance(key, slice):
        return self.__class__(order=a)
    else:
        return a
except IndexError:
    raise ItemNotFoundError(f"index {key} item not found")
```

#### \__setitem__(key: int | slice, value: Any) -> None

Sets an item or slice of items in the progression.

```python
a = validate_order(value)
self.order[key] = a
self.order = to_list(self.order, flatten=True)
```

This method allows for updating single items or slices of the progression, ensuring that the new values are valid Lion IDs.

#### \__len__() -> int

Returns the number of items in the progression.

```python
return len(self.order)
```

#### \__iter__() -> Iterator[str]

Returns an iterator over the items in the progression.

```python
return iter(self.order)
```

### Manipulation Methods

#### append(item: Any) -> None

Appends an item to the end of the progression.

```python
item_ = validate_order(item)
self.order.extend(item_)
```

#### include(item: Any)

Includes item(s) in the progression if not already present.

```python
item_ = validate_order(item)
for i in item_:
    if i not in self.order:
        self.order.append(i)
```

#### exclude(item: int | Any)

Excludes an item or items from the progression.

```python
for i in validate_order(item):
    while i in self:
        self.remove(i)
```

#### remove(item: Any) -> None

Removes the next occurrence of an item from the progression.

```python
if item in self:
    item = validate_order(item)
    l_ = list(self.order)

    with contextlib.suppress(ValueError):
        for i in item:
            l_.remove(i)
        self.order = l_
        return

raise ItemNotFoundError(f"{item}")
```

#### insert(index: int, item: Any) -> None

Inserts an item at the specified index.

```python
item_ = validate_order(item)
for i in reversed(item_):
    self.order.insert(index, SysUtil.get_id(i))
```

### Arithmetic Operations

#### \__add__(other: Any) -> Progression

Adds an item or items to the end of the progression.

```python
p1 + p2
```

#### \__iadd__(other: Any) -> Progression

Adds an item to the end of the progression in-place.

```python
p1 += p2
```

## Usage Examples

### Basic Usage

```python
from lion_core.generic import Node, Progression as prog


# Creating a Progression
p = prog([Node(value=1), Node(value=2)], name="Test")

print(str(p))
# Output: 'Progression(name=Test, size=2, items=['ln_...', 'ln_...'])'

# Using __contains__
print(Node(value=1) in p)  # Output: True

# Using __getitem__
print(p[0])  # Output: 'ln_...' (the Lion ID of the first element)

# Using __setitem__
p[1] = Node(value=3)
print(p[1])  # Output: 'ln_...' (the Lion ID of the new element)

# Using append
p.append(Node(value=4))
print(len(p))  # Output: 3
```

### Advanced Operations

```python
# Creating two Progressions
p1 = prog([Node(value=1), Node(value=2)], name="Prog1")
p2 = prog([Node(value=3), Node(value=4)], name="Prog2")

# Using __add__
combined = p1 + p2
print(str(combined))
# Output: 'Progression(name=None, size=4, items=['ln_...', 'ln_...', 'ln_...', 'ln_...'])'

# Using __iadd__
p1 += [Node(value=5), Node(value=6)]
print(str(p1))
# Output: 'Progression(name=Prog1, size=4, items=['ln_...', 'ln_...', 'ln_...', 'ln_...'])'

# Using slicing
sliced = p1[1:3]
print(str(sliced))
# Output: 'Progression(name=None, size=2, items=['ln_...', 'ln_...'])'

# Using insert
p1.insert(1, Node(value=7))
print(str(p1))
# Output: 'Progression(name=Prog1, size=5, items=['ln_...', 'ln_...', 'ln_...', 'ln_...', 'ln_...'])'
```

## Important Notes

1. The `Progression` class operates on Lion IDs, not actual Element objects.
2. It provides both mutable (in-place) and immutable operations.
3. Printed representations show truncated Lion IDs for readability.
4. The class is optimized for Lion ID operations, which may affect performance with large datasets.
5. `__setitem__` allows for updating both single items and slices, ensuring type consistency.

## Conclusion

The Progression class is a versatile tool in the Lion framework, offering powerful capabilities for managing ordered sequences of items via their Lion IDs. Its combination of list-like functionality and Lion-specific features makes it suitable for a wide range of use cases within the framework.