"""
Utilities for flattening nested data structures.

This module provides functions to flatten nested dictionaries or lists into
single-level dictionaries and to retrieve flattened keys from nested structures.

Functions:
    flatten: Flatten a nested data structure into a single-level dictionary.
    get_flattened_keys: Get all keys from a flattened representation of nested data.
"""

from typing import Any, Dict, Generator, Optional, Tuple

from .to_list import to_list
from .to_dict import to_dict

DEFAULT_SEPARATOR = '|'

def flatten(
    data: Any,
    parent_key: str = "",
    separator: str = DEFAULT_SEPARATOR,
    max_depth: Optional[int] = None,
    in_place: bool = False,
    flatten_dicts_only: bool = False,
) -> Optional[Dict[str, Any]]:
    """
    Flatten a nested data structure into a single-level dictionary.

    Args:
        data: The nested structure to flatten.
        parent_key: The base key to use for flattened keys. Defaults to "".
        separator: The separator to use for joining keys. Defaults to "|".
        max_depth: The maximum depth to flatten. Defaults to None (no limit).
        in_place: If True, modifies the original structure. Defaults to False.
        flatten_dicts_only: If True, only flattens dictionaries. Defaults to False.

    Returns:
        The flattened dictionary if in_place is False, otherwise None.

    Raises:
        TypeError: If in_place is True and data is not a dictionary.

    Examples:
        >>> nested = {'a': 1, 'b': {'c': 2, 'd': {'e': 3}}}
        >>> flatten(nested)
        {'a': 1, 'b|c': 2, 'b|d|e': 3}
    """
    if in_place:
        if not isinstance(data, dict):
            raise TypeError("Data must be a dictionary when 'in_place' is True.")
        _flatten_in_place(
            data,
            parent_key=parent_key,
            separator=separator,
            max_depth=max_depth,
            flatten_dicts_only=flatten_dicts_only,
        )
        return None
    
    flattened = to_dict(
        _flatten_generator(
            data,
            parent_key=tuple(parent_key.split(separator)) if parent_key else (),
            separator=separator,
            max_depth=max_depth,
            flatten_dicts_only=flatten_dicts_only,
        )
    )
    return flattened


def get_flattened_keys(
    data: Any,
    separator: str = DEFAULT_SEPARATOR,
    max_depth: Optional[int] = None,
    flatten_dicts_only: bool = False,
) -> list[str]:
    """
    Get all keys from a flattened representation of nested data.

    Args:
        data: The nested structure to process.
        separator: The separator to use for joining keys. Defaults to "|".
        max_depth: The maximum depth to flatten. Defaults to None (no limit).
        flatten_dicts_only: If True, only flattens dictionaries. Defaults to False.

    Returns:
        A list of flattened keys.

    Examples:
        >>> nested = {'a': 1, 'b': {'c': 2, 'd': {'e': 3}}}
        >>> get_flattened_keys(nested)
        ['a', 'b|c', 'b|d|e']
    """
    flattened = flatten(
        data,
        separator=separator,
        max_depth=max_depth,
        flatten_dicts_only=flatten_dicts_only
    )
    return to_list(flattened.keys())


def _flatten_in_place(
    data: Dict[str, Any],
    parent_key: str = "",
    separator: str = DEFAULT_SEPARATOR,
    max_depth: Optional[int] = None,
    current_depth: int = 0,
    flatten_dicts_only: bool = False,
) -> None:
    """
    Recursively flatten a nested dictionary in place.

    Args:
        data: The nested dictionary to flatten.
        parent_key: The base key to use for flattened keys.
        separator: The separator to use for joining keys.
        max_depth: The maximum depth to flatten.
        current_depth: The current depth of recursion.
        flatten_dicts_only: If True, only flattens dictionaries.
    """
    if max_depth is not None and current_depth >= max_depth:
        return

    keys_to_remove = []
    new_keys = {}

    for key, value in data.items():
        new_key = f"{parent_key}{separator}{key}" if parent_key else key

        if isinstance(value, dict):
            _flatten_in_place(
                value,
                parent_key=new_key,
                separator=separator,
                max_depth=max_depth,
                current_depth=current_depth + 1,
                flatten_dicts_only=flatten_dicts_only,
            )
            keys_to_remove.append(key)
            new_keys.update(value)
        elif not flatten_dicts_only and isinstance(value, list):
            flattened_list = {}
            for i, item in enumerate(value):
                list_key = f"{new_key}{separator}{i}"
                if isinstance(item, dict):
                    _flatten_in_place(
                        item,
                        parent_key=list_key,
                        separator=separator,
                        max_depth=max_depth,
                        current_depth=current_depth + 1,
                        flatten_dicts_only=flatten_dicts_only,
                    )
                    flattened_list.update(item)
                else:
                    flattened_list[list_key] = item
            keys_to_remove.append(key)
            new_keys.update(flattened_list)
        elif parent_key:
            new_keys[new_key] = value
            keys_to_remove.append(key)

    for key in keys_to_remove:
        del data[key]
    data.update(new_keys)


def _flatten_generator(
    data: Any,
    parent_key: Tuple[str, ...] = (),
    separator: str = DEFAULT_SEPARATOR,
    max_depth: Optional[int] = None,
    current_depth: int = 0,
    flatten_dicts_only: bool = False,
) -> Generator[Tuple[str, Any], None, None]:
    """
    Generator to recursively flatten a nested structure.

    Args:
        data: The nested structure to flatten.
        parent_key: The base key to use for flattened keys.
        separator: The separator to use for joining keys.
        max_depth: The maximum depth to flatten.
        current_depth: The current depth of recursion.
        flatten_dicts_only: If True, only flattens dictionaries.

    Yields:
        The flattened key and value pairs.
    """
    if max_depth is not None and current_depth >= max_depth:
        yield separator.join(parent_key), data
        return

    if isinstance(data, dict):
        for key, value in data.items():
            new_key = parent_key + (key,)
            yield from _flatten_generator(
                value, new_key, separator, max_depth, current_depth + 1, flatten_dicts_only
            )
    elif isinstance(data, list) and not flatten_dicts_only:
        for i, item in enumerate(data):
            new_key = parent_key + (str(i),)
            yield from _flatten_generator(
                item, new_key, separator, max_depth, current_depth + 1, flatten_dicts_only
            )
    else:
        yield separator.join(parent_key), data
        
        
