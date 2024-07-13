"""
Module for setting values in nested structures.

Provides functionality to set values deep within nested dictionaries or lists
using a specified path of indices. Ensures intermediate structures are created
as needed.
"""

from typing import Any, Sequence

from lion_core.libs.data_handlers._to_list import to_list
from lion_core.util import LN_UNDEFINED


def nset(
    nested_structure: dict[str, Any] | list[Any],
    indices: str | int | Sequence[str | int],
    value: Any,
) -> None:
    """
    Set a value within a nested structure at the specified path defined by indices.

    This method allows setting a value deep within a nested dictionary or list by
    specifying a path to the target location using a sequence of indices. Each index
    in the sequence represents a level in the nested structure, with integers used
    for list indices and strings for dictionary keys.

    Args:
        nested_structure: The nested structure where the value will be set.
        indices: The path of indices leading to where the value should be set.
        value: The value to set at the specified location in the nested structure.

    Raises:
        ValueError: If the indices sequence is empty.
        TypeError: If the target container is not a list or dictionary, or if
                   the index type is incorrect.

    Examples:
        >>> data = {'a': {'b': [10, 20]}}
        >>> nset(data, ['a', 'b', 1], 99)
        >>> assert data == {'a': {'b': [10, 99]}}

        >>> data = [0, [1, 2], 3]
        >>> nset(data, [1, 1], 99)
        >>> assert data == [0, [1, 99], 3]
    """
    if not indices:
        raise ValueError("Indices list is empty, cannot determine target container")

    _indices = to_list(indices)
    target_container = nested_structure

    for i, index in enumerate(_indices[:-1]):
        if isinstance(target_container, list):
            if not isinstance(index, int):
                raise TypeError("Cannot use non-integer index on a list")
            ensure_list_index(target_container, index)
            if target_container[index] is None:
                next_index = _indices[i + 1]
                target_container[index] = [] if isinstance(next_index, int) else {}
        elif isinstance(target_container, dict):
            if isinstance(index, int):
                raise TypeError(
                    f"Unsupported key type: {type(index).__name__}. Only string keys are acceptable."
                )
            if index not in target_container:
                next_index = _indices[i + 1]
                target_container[index] = [] if isinstance(next_index, int) else {}
        else:
            raise TypeError("Target container is not a list or dictionary")

        target_container = target_container[index]

    last_index = _indices[-1]
    if isinstance(target_container, list):
        if not isinstance(last_index, int):
            raise TypeError("Cannot use non-integer index on a list")
        ensure_list_index(target_container, last_index)
        target_container[last_index] = value
    elif isinstance(target_container, dict):
        if isinstance(last_index, int):
            raise TypeError(
                f"Unsupported key type: {type(last_index).__name__}. Only string keys are acceptable."
            )
        target_container[last_index] = value
    else:
        raise TypeError("Cannot set value on non-list/dict element")


def ensure_list_index(lst: list[Any], index: int, default: Any = LN_UNDEFINED) -> None:
    """
    Extend a list to ensure it has a minimum length, appending a default value as needed.

    This utility method ensures that a list is extended to at least a specified
    index plus one. If the list's length is less than this target, it is appended
    with a specified default value until it reaches the required length.

    Args:
        lst: The list to extend.
        index: The target index that the list should reach or exceed.
        default: The value to append to the list for extension. Defaults to None.

    Note:
        Modifies the list in place, ensuring it can safely be indexed at `index`
        without raising an IndexError.
    """
    while len(lst) <= index:
        lst.append(default if default is not LN_UNDEFINED else None)


# Path: lion_core/libs/data_handlers/_nset.py
