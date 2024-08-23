from collections.abc import Iterable, Mapping, Sequence
from functools import singledispatch
from typing import Any, TypeVar

from pydantic import BaseModel

from lion_core.setting import LionUndefined

T = TypeVar("T")


@singledispatch
def to_list(
    input_: Any, /, *, flatten: bool = False, dropna: bool = False
) -> list[Any]:
    """Convert various input types to a list.

    Handles different input types and converts them to a list,
    with options for flattening nested structures and removing None values.

    Accepted input types and behaviors:
    1. None or LionUndefined: Returns an empty list [].
    2. str, bytes, bytearray: Returns a single-item list with the input.
    3. Mapping (dict, etc.): Returns a single-item list with the input.
    4. BaseModel: Returns a single-item list with the input.
    5. Sequence (list, tuple, etc.):
       - If flatten=False, returns the sequence as a list.
       - If flatten=True, flattens nested sequences.
    6. Other Iterables: Converts to a list, flattens if specified.
    7. Any other type: Returns a single-item list with the input.

    Args:
        input_: The input to be converted to a list.
        flatten: If True, flattens nested list structures.
        dropna: If True, removes None values from the result.

    Returns:
        A list derived from the input, processed as specified.

    Examples:
        >>> to_list(1)
        [1]
        >>> to_list([1, [2, 3]], flatten=True)
        [1, 2, 3]
        >>> to_list([1, None, 2], dropna=True)
        [1, 2]
    """
    return [input_]


@to_list.register(LionUndefined)
@to_list.register(type(None))
def _(input_: None | LionUndefined, /, **kwargs: Any) -> list[Any]:
    """Handle None and LionUndefined inputs."""
    return []


@to_list.register(str)
@to_list.register(bytes)
@to_list.register(bytearray)
@to_list.register(Mapping)
@to_list.register(BaseModel)
def _(
    input_: str | bytes | bytearray | Mapping | BaseModel, /, **kwargs: Any
) -> list[Any]:
    """Handle string-like, Mapping, and BaseModel inputs."""
    return [input_]


@to_list.register(Sequence)
@to_list.register(Iterable)
def _(
    input_: Sequence[T] | Iterable[T],
    /,
    *,
    flatten: bool = False,
    dropna: bool = False,
) -> list[T]:
    """Handle Sequence and Iterable inputs.

    Converts the input to a list and optionally flattens and removes None
    """
    result = list(input_)
    return (
        _process_list(result, flatten, dropna) if flatten or dropna else result
    )


def _process_list(lst: list[Any], flatten: bool, dropna: bool) -> list[Any]:
    """Process a list by optionally flattening and removing None values.

    Args:
        lst: The list to process.
        flatten: If True, flattens nested list structures.
        dropna: If True, removes None values.

    Returns:
        The processed list.
    """
    result = []
    for item in lst:
        if isinstance(item, Iterable) and not isinstance(
            item, (str, bytes, bytearray, Mapping)
        ):
            if flatten:
                result.extend(_process_list(list(item), flatten, dropna))
            else:
                result.append(_process_list(list(item), flatten, dropna))
        elif not dropna or item is not None:
            result.append(item)
    return result


# File: lion_core/libs/data_handlers/_to_list.py
