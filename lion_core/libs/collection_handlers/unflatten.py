"""
Utilities for unflattening data structures.

This module provides functionality to unflatten a single-level dictionary into
a nested dictionary or list structure.

Functions:
    unflatten: Unflatten a single-level dictionary into a nested structure.
"""

from typing import Any, Dict, Optional

DEFAULT_SEPARATOR = '|'


def unflatten(
    data: Dict[str, Any],
    parent_key: str = "",
    separator: str = DEFAULT_SEPARATOR,
    max_depth: Optional[int] = None,
    unflatten_in_place: bool = False,
    unflatten_lists: bool = True,
) -> Optional[Dict[str, Any]]:
    """
    Unflatten a single-level dictionary into a nested dictionary or list.

    Args:
        data: The flattened dictionary to unflatten.
        parent_key: The base key to use for unflattening. Defaults to "".
        separator: The separator used for joining keys. Defaults to "|".
        max_depth: The maximum depth to unflatten. Defaults to None (no limit).
        unflatten_in_place: If True, modifies the original structure. Defaults
                            to False.
        unflatten_lists: If True, converts dict to list when keys are
                         consecutive integers. Defaults to True.

    Returns:
        The unflattened nested dictionary if unflatten_in_place is False,
        otherwise None.

    Raises:
        TypeError: If unflatten_in_place is True and data is not a dictionary.

    Examples:
        >>> flat = {'a': 1, 'b|c': 2, 'b|d|e': 3}
        >>> unflatten(flat)
        {'a': 1, 'b': {'c': 2, 'd': {'e': 3}}}
    """
    if unflatten_in_place:
        if not isinstance(data, dict):
            raise TypeError(
                "Data must be a dictionary when 'unflatten_in_place' is True."
            )
        _unflatten_in_place(
            data,
            parent_key=parent_key,
            separator=separator,
            max_depth=max_depth,
            unflatten_lists=unflatten_lists,
        )
        return None

    return _unflatten_generator(
        data,
        parent_key=parent_key.split(separator) if parent_key else [],
        separator=separator,
        max_depth=max_depth,
        unflatten_lists=unflatten_lists,
    )


def _unflatten_in_place(
    data: Dict[str, Any],
    parent_key: str = "",
    separator: str = DEFAULT_SEPARATOR,
    max_depth: Optional[int] = None,
    current_depth: int = 0,
    unflatten_lists: bool = True,
) -> None:
    """
    Recursively unflatten a dictionary in place.

    Args:
        data: The dictionary to unflatten.
        parent_key: The base key to use for unflattening.
        separator: The separator used for joining keys.
        max_depth: The maximum depth to unflatten.
        current_depth: The current depth of recursion.
        unflatten_lists: If True, converts dict to list when keys are
                         consecutive integers.
    """
    if max_depth is not None and current_depth >= max_depth:
        return

    keys_to_remove = []
    new_keys = {}

    for key, value in data.items():
        if separator in key:
            parts = key.split(separator)
            new_key = parts[0]
            remaining_key = separator.join(parts[1:])

            if new_key not in new_keys:
                new_keys[new_key] = {}

            new_keys[new_key][remaining_key] = value
            keys_to_remove.append(key)

    for key in keys_to_remove:
        del data[key]

    for key, nested_dict in new_keys.items():
        _unflatten_in_place(
            nested_dict,
            separator=separator,
            max_depth=max_depth,
            current_depth=current_depth + 1,
            unflatten_lists=unflatten_lists,
        )
        if unflatten_lists and all(k.isdigit() for k in nested_dict.keys()):
            data[key] = [nested_dict[str(i)] for i in range(len(nested_dict))]
        else:
            data[key] = nested_dict


def _unflatten_generator(
    data: Dict[str, Any],
    parent_key: list = [],
    separator: str = DEFAULT_SEPARATOR,
    max_depth: Optional[int] = None,
    current_depth: int = 0,
    unflatten_lists: bool = True,
) -> Dict[str, Any]:
    """
    Generator to recursively unflatten a dictionary.

    Args:
        data: The dictionary to unflatten.
        parent_key: The base key to use for unflattening.
        separator: The separator used for joining keys.
        max_depth: The maximum depth to unflatten.
        current_depth: The current depth of recursion.
        unflatten_lists: If True, converts dict to list when keys are
                         consecutive integers.

    Returns:
        The unflattened nested dictionary.
    """
    result = {}

    if max_depth is not None and current_depth >= max_depth:
        return {separator.join(parent_key): data}

    for key, value in data.items():
        key_parts = key.split(separator)
        current = result

        for part in key_parts[:-1]:
            if part not in current:
                current[part] = {}
            current = current[part]

        current[key_parts[-1]] = value

    if unflatten_lists:
        for key, value in result.items():
            if isinstance(value, dict) and all(k.isdigit() for k in value):
                result[key] = [value[str(i)] for i in range(len(value))]
            elif isinstance(value, dict):
                result[key] = _unflatten_generator(
                    value,
                    separator=separator,
                    max_depth=max_depth,
                    current_depth=current_depth + 1,
                    unflatten_lists=unflatten_lists,
                )

    return result