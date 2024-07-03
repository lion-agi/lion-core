"""
Module for inserting values into nested structures.

Provides functionality to insert values into nested dictionaries or lists at
specified paths, with support for creating intermediate structures as needed.

Functions:
    ninsert: Inserts a value into a nested structure at a specified path.
    handle_list_insert: Ensures a specified index in a list is occupied by a
                        given value, extending the list if necessary.
"""

from lion_core.libs.data_handlers._to_list import to_list
from typing import Any, Union


def ninsert(
    nested_structure: Union[dict, list],
    indices: list[Union[str, int]],
    value: Any,
    *,
    current_depth: int = 0,
) -> None:
    """
    Inserts a value into a nested structure at a specified path.

    Navigates a nested dictionary or list based on a sequence of indices or keys
    (`indices`) and inserts `value` at the final location. This method can create
    intermediate dictionaries or lists as needed.

    Args:
        nested_structure (dict | list): The nested structure to modify.
        indices (list[str | int]): The sequence of keys (str for dicts) or
            indices (int for lists) defining the path to the insertion point.
        value (Any): The value to insert at the specified location within
            `nested_structure`.
        current_depth (int): Internal use only; tracks the current depth
            during recursive calls.

    Examples:
        >>> subject_ = {'a': {'b': [1, 2]}}
        >>> ninsert(subject_, ['a', 'b', 2], 3)
        >>> assert subject_ == {'a': {'b': [1, 2, 3]}}

        >>> subject_ = []
        >>> ninsert(subject_, [0, 'a'], 1)
        >>> assert subject_ == [{'a': 1}]
    """
    if not indices:
        raise ValueError("Indices list cannot be empty")

    indices = to_list(indices)
    for i, part in enumerate(indices[:-1]):
        if isinstance(part, int):
            if isinstance(nested_structure, dict):
                raise TypeError(f"Unsupported key type: {type(part).__name__}. Only string keys are acceptable.")
            while len(nested_structure) <= part:
                nested_structure.append(None)
            if nested_structure[part] is None or not isinstance(
                nested_structure[part], (dict, list)
            ):
                next_part = indices[i + 1]
                nested_structure[part] = [] if isinstance(next_part, int) else {}
        elif isinstance(nested_structure, dict):
            if part not in nested_structure:
                next_part = indices[i + 1]
                nested_structure[part] = [] if isinstance(next_part, int) else {}
        else:
            raise TypeError("Invalid container type encountered during insertion")

        nested_structure = nested_structure[part]
        current_depth += 1

    last_part = indices[-1]
    if isinstance(last_part, int):
        if isinstance(nested_structure, dict):
            raise TypeError(f"Unsupported key type: {type(last_part).__name__}. Only string keys are acceptable.")
        while len(nested_structure) <= last_part:
            nested_structure.append(None)
        nested_structure[last_part] = value
    elif isinstance(nested_structure, list):
        raise TypeError("Cannot use non-integer index on a list")
    else:
        nested_structure[last_part] = value
        
        
# Path: lion_core/libs/data_handlers/_ninsert.py