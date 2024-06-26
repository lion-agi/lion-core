"""
Utilities for retrieving values from nested data structures.

This module provides a function to retrieve a value from a nested dictionary
or list using a list of indices.

Functions:
    get_nested: Retrieve a value from a nested structure using a list of indices.
"""

from typing import Any, Union

from .utils import get_target_container


def get_nested(
    data: Union[dict, list],
    indices: list[Union[int, str]],
    default: Any = ...,
) -> Any:
    """
    Retrieve a value from a nested structure using a list of indices.

    This function navigates through a nested dictionary or list based on the
    provided indices and returns the value found at the target location. If the
    target value is not found, a default value can be returned, or a LookupError
    can be raised.

    Args:
        data: The nested structure to retrieve the value from.
        indices: A list of indices to navigate through the nested structure.
        default: The default value to return if the target value is not found.
                 If not provided, a LookupError is raised.

    Returns:
        The value retrieved from the nested structure, or the default value
        if provided.

    Raises:
        LookupError: If the target value is not found and no default value
                     is provided.

    Examples:
        >>> nested = {'a': {'b': [1, 2, {'c': 3}]}}
        >>> get_nested(nested, ['a', 'b', 2, 'c'])
        3
        >>> get_nested(nested, ['a', 'b', 3], default=None)
        None
    """
    try:
        target_container = get_target_container(data, indices[:-1])
        last_index = indices[-1]

        if (isinstance(target_container, list) and
            isinstance(last_index, int) and
            last_index < len(target_container)):
            return target_container[last_index]
        elif isinstance(target_container, dict) and last_index in target_container:
            return target_container[last_index]
        elif default is not ...:
            return default
        else:
            raise LookupError("Target not found and no default value provided.")
    except (IndexError, KeyError, TypeError):
        if default is not ...:
            return default
        else:
            raise LookupError("Target not found and no default value provided.")