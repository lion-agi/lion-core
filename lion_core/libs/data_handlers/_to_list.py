from collections.abc import Iterable, Mapping, Sequence
from typing import Any, TypeVar, overload

from pydantic import BaseModel
from pydantic_core import PydanticUndefined, PydanticUndefinedType

from lion_core.setting import LN_UNDEFINED, LionUndefinedType

T = TypeVar("T")


@overload
def to_list(
    input_: None | LionUndefinedType | PydanticUndefinedType, /
) -> list[Any]: ...


@overload
def to_list(
    input_: str | bytes | bytearray | Mapping | BaseModel,
    /,
) -> list[Any]: ...


@overload
def to_list(
    input_: Sequence[T] | Iterable[T],
    /,
    *,
    flatten: bool = False,
    dropna: bool = False,
    unique: bool = False,
) -> list[T]: ...


@overload
def to_list(
    input_: Any,
    /,
    *,
    flatten: bool = False,
    dropna: bool = False,
    unique: bool = False,
) -> list[Any]: ...


def to_list(
    input_: Any,
    /,
    *,
    flatten: bool = False,
    dropna: bool = False,
    unique: bool = False,
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
    return _dispatch_to_list(
        input_,
        flatten=flatten,
        dropna=dropna,
        unique=unique,
    )


def _dispatch_to_list(input_: Any, /, **kwargs: Any) -> list[Any]:

    if input_ in [LN_UNDEFINED, PydanticUndefined, None, [], {}]:
        return []

    if isinstance(input_, str | bytes | bytearray | Mapping | BaseModel):
        return [input_]

    if isinstance(input_, Sequence | Iterable):
        return _process_iterable(input_, **kwargs)

    return [input_]


def _process_iterable(
    input_: Sequence[T] | Iterable[T],
    /,
    *,
    flatten: bool,
    dropna: bool,
    unique: bool,
) -> list[T]:
    """Handle Sequence and Iterable inputs.

    Converts the input to a list and optionally flattens and removes None
    """
    result = list(input_)
    if any((flatten, dropna, unique)):
        return _process_list(
            lst=result,
            flatten=flatten,
            dropna=dropna,
            unique=unique,
        )
    return result


def _process_list(
    lst: list[Any], flatten: bool, dropna: bool, unique: bool
) -> list[Any]:
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
                result.extend(
                    _process_list(
                        lst=list(item),
                        flatten=flatten,
                        dropna=dropna,
                        unique=unique,
                    )
                )
            else:
                result.append(
                    _process_list(
                        lst=list(item),
                        flatten=flatten,
                        dropna=dropna,
                        unique=unique,
                    )
                )
        elif not dropna or item is not None:
            result.append(item)
    return list(set(result)) if unique else result


# File: lion_core/libs/data_handlers/_to_list.py
