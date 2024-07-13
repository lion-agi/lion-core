"""
Module for converting various input types into lists.

Provides functions to convert a variety of data structures into lists,
with options for flattening nested lists and removing None values.
"""

from collections.abc import Mapping, Iterable
from typing import Any, Generator

from pydantic import BaseModel


def to_list(
    input_: Any, /, *, flatten: bool = False, dropna: bool = False
) -> list[Any]:
    """
    Convert various types of input into a list.

    Args:
        input_: The input to convert to a list.
        flatten: If True, flattens nested lists.
        dropna: If True, removes None values.

    Returns:
        The converted list.

    Examples:
        >>> to_list(1)
        [1]
        >>> to_list([1, 2, [3, 4]], flatten=True)
        [1, 2, 3, 4]
        >>> to_list([1, None, 2], dropna=True)
        [1, 2]
    """
    if input_ is None:
        return []

    if not isinstance(input_, Iterable) or isinstance(
        input_, (str, bytes, bytearray, Mapping, BaseModel)
    ):
        return [input_]

    iterable_list = list(input_) if not isinstance(input_, list) else input_

    return flatten_list(iterable_list, dropna) if flatten else iterable_list


def flatten_list(lst_: list[Any], dropna: bool = True) -> list[Any]:
    """
    Flatten a nested list.

    Args:
        lst: The list to flatten.
        dropna: If True, removes None values.

    Returns:
        The flattened list.

    Examples:
        >>> flatten_list([1, [2, 3], [4, [5, 6]]])
        [1, 2, 3, 4, 5, 6]
        >>> flatten_list([1, None, 2], dropna=True)
        [1, 2]
    """
    flattened_list = list(_flatten_list_generator(lst_, dropna))
    return [i for i in flattened_list if i is not None] if dropna else flattened_list


def _flatten_list_generator(
    lst_: Iterable[Any], dropna: bool = True
) -> Generator[Any, None, None]:
    """
    A generator to recursively flatten a nested list.

    Args:
        lst: The list to flatten.
        dropna: If True, removes None values.

    Yields:
        The next flattened element from the list.

    Examples:
        >>> list(_flatten_list_generator([1, [2, 3], [4, [5, 6]]]))
        [1, 2, 3, 4, 5, 6]
    """
    for i in lst_:
        if isinstance(i, Iterable) and not isinstance(
            i, (str, bytes, bytearray, Mapping)
        ):
            yield from _flatten_list_generator(i, dropna)
        else:
            yield i


# Path: lion_core/libs/data_handlers/_to_list.py
