from collections.abc import Callable
from typing import Any


def nfilter(
    nested_structure: dict[Any, Any] | list[Any],
    condition: Callable[[Any], bool],
) -> dict[Any, Any] | list[Any]:
    """
    Filter elements in a nested structure (dict or list) based on a condition.

    Args:
        nested_structure: The nested structure to filter.
        condition: A function that returns True for elements to keep and
            False for elements to discard.

    Returns:
        The filtered nested structure.

    Raises:
        TypeError: If nested_structure is not a dict or list.
    """
    if isinstance(nested_structure, dict):
        return _filter_dict(nested_structure, condition)
    elif isinstance(nested_structure, list):
        return _filter_list(nested_structure, condition)
    else:
        raise TypeError(
            "The nested_structure must be either a dict or a list."
        )


def _filter_dict(
    dictionary: dict[Any, Any], condition: Callable[[tuple[Any, Any]], bool]
) -> dict[Any, Any]:
    """
    Filter elements in a dictionary based on a condition.

    Args:
        dictionary: The dictionary to filter.
        condition: A function that returns True for key-value pairs to keep
            and False for key-value pairs to discard.

    Returns:
        The filtered dictionary.
    """
    return {
        k: nfilter(v, condition) if isinstance(v, dict | list) else v
        for k, v in dictionary.items()
        if condition(v) or isinstance(v, dict | list)
    }


def _filter_list(
    lst: list[Any], condition: Callable[[Any], bool]
) -> list[Any]:
    """
    Filter elements in a list based on a condition.

    Args:
        lst: The list to filter.
        condition: A function that returns True for elements to keep and
            False for elements to discard.

    Returns:
        The filtered list.
    """
    return [
        nfilter(item, condition) if isinstance(item, dict | list) else item
        for item in lst
        if condition(item) or isinstance(item, dict | list)
    ]


# Path: lion_core/libs/data_handlers/_nfilter.py
