"""
Utilities for filtering nested data structures.

This module provides functions to filter elements in nested structures
(dictionaries or lists) based on a given condition.

Functions:
    filter_nested: Filter elements in a nested structure based on a condition.
"""

from typing import Any, Callable, Union


def filter_nested(
    data: Union[dict, list],
    condition: Callable[[Any], bool]
) -> Union[dict, list]:
    """
    Filter elements in a nested structure (dict or list) based on a condition.

    Args:
        data: The nested structure to filter.
        condition: A function that returns True for elements to keep and
                   False for elements to discard.

    Returns:
        The filtered nested structure.

    Raises:
        TypeError: If data is not a dict or list.

    Examples:
        >>> nested = {'a': 1, 'b': {'c': 2, 'd': 3}, 'e': [4, 5, 6]}
        >>> filter_nested(nested, lambda x: isinstance(x, int) and x % 2 == 0)
        {'b': {'c': 2}, 'e': [4, 6]}
    """
    if isinstance(data, dict):
        return _filter_dict(data, condition)
    elif isinstance(data, list):
        return _filter_list(data, condition)
    else:
        raise TypeError("The data must be either a dict or a list.")


def _filter_dict(
    data: dict[Any, Any],
    condition: Callable[[Any], bool]
) -> dict[Any, Any]:
    """
    Filter elements in a dictionary based on a condition.

    Args:
        data: The dictionary to filter.
        condition: A function that returns True for elements to keep and
                   False for elements to discard.

    Returns:
        The filtered dictionary.
    """
    return {
        k: filter_nested(v, condition) if isinstance(v, (dict, list)) else v
        for k, v in data.items()
        if condition(v) or isinstance(v, (dict, list))
    }


def _filter_list(
    data: list[Any],
    condition: Callable[[Any], bool]
) -> list[Any]:
    """
    Filter elements in a list based on a condition.

    Args:
        data: The list to filter.
        condition: A function that returns True for elements to keep and
                   False for elements to discard.

    Returns:
        The filtered list.
    """
    return [
        filter_nested(item, condition) if isinstance(item, (dict, list)) else item
        for item in data
        if condition(item) or isinstance(item, (dict, list))
    ]