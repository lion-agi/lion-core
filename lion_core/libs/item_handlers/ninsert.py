"""
Module for inserting values into nested structures.

Provides functionality to insert values into nested dictionaries or lists at
specified paths, with support for creating intermediate structures as needed.

Functions:
    ninsert: Inserts a value into a nested structure at a specified path.
    handle_list_insert: Ensures a specified index in a list is occupied by a
                        given value, extending the list if necessary.
"""

from typing import Any, Union

from .to_list import to_list


def ninsert(
    nested_structure: Union[dict, list],
    indices: list[Union[str, int]],
    value: Any,
    *,
    sep: str = "|",
    max_depth: Union[int, None] = None,
    current_depth: int = 0,
) -> None:
    """
    Inserts a value into a nested structure at a specified path.

    Args:
        nested_structure: The nested structure to modify.
        indices: The sequence of keys or indices defining the insertion path.
        value: The value to insert at the specified location.
        sep: A separator for concatenating indices. Defaults to "|".
        max_depth: Limits the depth of insertion. If None, no limit is applied.
        current_depth: Internal use only; tracks the current depth.

    Raises:
        ValueError: If the indices list is empty.
        TypeError: If an invalid container type is encountered.

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

    if isinstance(indices, str):
        indices = indices.split(sep)
    indices = to_list(indices)
    for i, part in enumerate(indices[:-1]):
        if max_depth is not None and current_depth >= max_depth:
            break

        if isinstance(part, int):
            while len(nested_structure) <= part:
                nested_structure.append(None)
            if nested_structure[part] is None or not isinstance(
                nested_structure[part], (dict, list)
            ):
                next_part = indices[i + 1]
                nested_structure[part] = (
                    [] if isinstance(next_part, int) else {}
                )
        elif isinstance(nested_structure, dict):
            if part not in nested_structure:
                next_part = indices[i + 1]
                nested_structure[part] = (
                    [] if isinstance(next_part, int) else {}
                )
        else:
            raise TypeError("Invalid container type encountered during insertion")

        nested_structure = nested_structure[part]
        current_depth += 1

    last_part = indices[-1]
    if max_depth is not None and current_depth >= max_depth:
        if isinstance(last_part, int):
            handle_list_insert(nested_structure, last_part, value)
        elif isinstance(nested_structure, list):
            raise TypeError("Cannot use non-integer index on a list")
        else:
            nested_structure[last_part] = value
    else:
        if isinstance(last_part, int):
            handle_list_insert(nested_structure, last_part, value)
        elif isinstance(nested_structure, list):
            raise TypeError("Cannot use non-integer index on a list")
        else:
            nested_structure[last_part] = value


def handle_list_insert(nested_structure: list, part: int, value: Any) -> None:
    """
    Ensures a specified index in a list is occupied by a given value.

    Args:
        nested_structure: The list to modify.
        part: The target index for inserting or replacing the value.
        value: The value to be inserted or to replace an existing value.

    Note:
        This function directly modifies the input list in place.
    """
    while len(nested_structure) <= part:
        nested_structure.append(None)
    nested_structure[part] = value