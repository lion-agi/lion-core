"""
Utilities for merging nested data structures.

This module provides functionality to merge multiple dictionaries, lists, or
sequences into a unified structure with options for handling duplicate keys,
sorting, and custom sorting logic.

Functions:
    merge_nested: Merge multiple dictionaries, lists, or sequences into a
                  unified structure.
"""

from collections import defaultdict
from itertools import chain
from typing import Any, Callable, Union, List

from .utils import is_homogeneous

def merge_nested(
    data: List[Union[dict, list]],
    /,
    *,
    overwrite: bool = False,
    sequence_keys: bool = False,
    separator: str = "|",
    sort_result: bool = False,
    sort_key: Callable[[Any], Any] | None = None,
) -> Union[dict, list]:
    """
    Merge multiple dictionaries, lists, or sequences into a unified structure.

    Args:
        data: A list containing dictionaries, lists, or other iterable objects
              to merge.
        overwrite: If True, overwrite existing keys in dictionaries with those
                   from subsequent dictionaries. Defaults to False.
        sequence_keys: Enables unique key generation for duplicate keys by
                       appending a sequence number, using `separator` as the
                       delimiter. Applicable only if `overwrite` is False.
        separator: The separator used when generating unique keys for duplicate
                   dictionary keys. Defaults to "|".
        sort_result: When True, sort the resulting list after merging. It does
                     not affect dictionaries. Defaults to False.
        sort_key: An optional callable that defines custom sorting logic for
                  the merged list. Defaults to None.

    Returns:
        A merged dictionary or list, depending on the types present in `data`.

    Raises:
        TypeError: If `data` contains objects of incompatible types that cannot
                   be merged.

    Examples:
        >>> dicts = [{'a': 1, 'b': 2}, {'b': 3, 'c': 4}]
        >>> merge_nested(dicts, overwrite=True)
        {'a': 1, 'b': 3, 'c': 4}

        >>> lists = [[1, 2], [3, 4], [5, 6]]
        >>> merge_nested(lists, sort_result=True)
        [1, 2, 3, 4, 5, 6]
    """
    if is_homogeneous(data, dict):
        return _merge_dicts(data, overwrite, sequence_keys, separator)
    elif is_homogeneous(data, list) and not any(
        isinstance(item, (dict, str)) for item in data
    ):
        return _merge_sequences(data, sort_result, sort_key)
    else:
        raise TypeError(
            "All items in the input list must be of the same type, "
            "either dict, list, or Iterable."
        )


def _deep_merge_dicts(dict1: dict, dict2: dict) -> dict:
    """
    Recursively merges two dictionaries, combining values where keys overlap.

    Args:
        dict1: The first dictionary.
        dict2: The second dictionary.

    Returns:
        The merged dictionary.
    """
    for key, value in dict2.items():
        if key in dict1:
            if isinstance(dict1[key], dict) and isinstance(value, dict):
                _deep_merge_dicts(dict1[key], value)
            else:
                if not isinstance(dict1[key], list):
                    dict1[key] = [dict1[key]]
                dict1[key].append(value)
        else:
            dict1[key] = value
    return dict1


def _merge_dicts(
    data: List[dict[Any, Any]],
    overwrite: bool,
    sequence_keys: bool,
    separator: str,
) -> dict[Any, Any]:
    """
    Merges a list of dictionaries into a single dictionary.

    Args:
        data: A list of dictionaries to merge.
        overwrite: If True, overwrite existing keys in dictionaries with those
                   from subsequent dictionaries.
        sequence_keys: Enables unique key generation for duplicate keys by
                       appending a sequence number, using `separator` as the
                       delimiter.
        separator: The separator used when generating unique keys for duplicate
                   dictionary keys.

    Returns:
        The merged dictionary.
    """
    merged = {}
    counters = defaultdict(int)

    for d in data:
        for key, value in d.items():
            if key not in merged or overwrite:
                if (
                    key in merged
                    and isinstance(merged[key], dict)
                    and isinstance(value, dict)
                ):
                    _deep_merge_dicts(merged[key], value)
                else:
                    merged[key] = value
            elif sequence_keys:
                counters[key] += 1
                new_key = f"{key}{separator}{counters[key]}"
                merged[new_key] = value
            else:
                if not isinstance(merged[key], list):
                    merged[key] = [merged[key]]
                merged[key].append(value)

    return merged


def _merge_sequences(
    data: list,
    sort_result: bool,
    sort_key: Callable[[Any], Any] | None = None,
) -> list[Any]:
    """
    Merges a list of lists into a single list.

    Args:
        data: A list of lists to merge.
        sort_result: When True, sort the resulting list after merging.
        sort_key: An optional callable that defines custom sorting logic for
                  the merged list.

    Returns:
        The merged list.
    """
    merged = list(chain(*data))
    if sort_result:
        return sorted(merged, key=sort_key or (lambda x: (isinstance(x, str), x)))
    return merged