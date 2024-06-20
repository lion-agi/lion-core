"""
Utilities for setting values in nested data structures.

This module provides functionality to set values deep within nested dictionaries
or lists using a specified path of indices. It ensures intermediate structures
are created as needed.

Functions:
    set_nested: Sets a value within a nested structure at a specified path.
    ensure_list_length: Extends a list to ensure it has a minimum length,
                        appending a default value as needed.
"""

from typing import Any, Union

from .to_list import to_list


def set_nested(
    data: Union[dict, list],
    indices: list[Union[int, str]],
    value: Any
) -> None:
    """
    Sets a value within a nested structure at the specified path.

    Args:
        data: The nested structure where the value will be set.
        indices: The path of indices leading to where the value should be set.
        value: The value to set at the specified location.

    Raises:
        ValueError: If the indices list is empty.
        TypeError: If the target container is not a list or dictionary,
                   or if the index type is incorrect.

    Examples:
        >>> nested = {'a': {'b': [10, 20]}}
        >>> set_nested(nested, ['a', 'b', 1], 99)
        >>> assert nested == {'a': {'b': [10, 99]}}

        >>> nested = [0, [1, 2], 3]
        >>> set_nested(nested, [1, 1], 99)
        >>> assert nested == [0, [1, 99], 3]
    """
    if not indices:
        raise ValueError("Indices list is empty, cannot determine target")

    _indices = to_list(indices)
    target = data

    for i, index in enumerate(_indices[:-1]):
        if isinstance(target, list):
            ensure_list_length(target, index)
            if target[index] is None:
                next_index = _indices[i + 1]
                target[index] = [] if isinstance(next_index, int) else {}
        elif isinstance(target, dict):
            if index not in target:
                next_index = _indices[i + 1]
                target[index] = [] if isinstance(next_index, int) else {}
        else:
            raise TypeError("Target container is not a list or dictionary")

        target = target[index]

    last_index = _indices[-1]
    if isinstance(target, list):
        ensure_list_length(target, last_index)
        target[last_index] = value
    elif isinstance(target, dict):
        target[last_index] = value
    else:
        raise TypeError("Cannot set value on non-list/dict element")


def ensure_list_length(lst: list, index: int, default: Any = None) -> None:
    """
    Extend a list to ensure it has a minimum length.

    Args:
        lst: The list to extend.
        index: The target index that the list should reach or exceed.
        default: The value to append to the list for extension.

    Note:
        Modifies the list in place, ensuring it can safely be indexed at
        `index` without raising an IndexError.
    """
    while len(lst) <= index:
        lst.append(default)