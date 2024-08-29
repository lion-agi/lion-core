from collections.abc import Iterable, Mapping
from typing import Any, TypeVar, overload

from pydantic_core import PydanticUndefinedType

from lion_core.setting import LionUndefinedType

T = TypeVar("T")


@overload
def to_list(
    input_: None | LionUndefinedType | PydanticUndefinedType, /
) -> list: ...


@overload
def to_list(
    input_: str | bytes | bytearray, /, use_values: bool = False
) -> list[str | int]: ...


@overload
def to_list(input_: Mapping, /, use_values: bool = False) -> list[Any]: ...


@overload
def to_list(
    input_: Any,
    /,
    *,
    flatten: bool = False,
    dropna: bool = False,
    unique: bool = False,
) -> list: ...


def to_list(
    input_: Any,
    /,
    *,
    flatten: bool = False,
    dropna: bool = False,
    unique: bool = False,
) -> list:
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
        unique: If True, returns only unique values. (only works
            with flatten=True)

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
    if unique and not flatten:
        raise ValueError("unique=True requires flatten=True")

    lst_ = _to_list_type(input_)

    if any((flatten, dropna)):
        lst_ = _process_list(
            lst=lst_,
            flatten=flatten,
            dropna=dropna,
        )

    return list(set(lst_)) if unique else lst_


def _undefined_to_list(
    input_: None | LionUndefinedType | PydanticUndefinedType, /
) -> list:
    return []


def _str_to_list(
    input_: str | bytes | bytearray, /, use_values: bool = False
) -> list[str | int]:
    if use_values:
        return list(input_)
    return [input_]


def _dict_to_list(input_: Mapping, /, use_values: bool = False) -> list[Any]:
    if use_values:
        return list(input_.values())
    return [input_]


def _to_list_type(input_: Any, /, use_values: bool = False) -> Any | None:

    if use_values and hasattr(input_, "values"):
        return list(input_.values())

    if isinstance(input_, list):
        return input_

    if isinstance(
        input_, type(None) | LionUndefinedType | PydanticUndefinedType
    ):
        return _undefined_to_list(input_)

    if isinstance(input_, str | bytes | bytearray):
        return _str_to_list(input_, use_values=use_values)

    if isinstance(input_, Mapping):
        return _dict_to_list(input_, use_values=use_values)

    if isinstance(input_, Iterable):
        return list(input_)

    return [input_]


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
                result.extend(
                    _process_list(
                        lst=list(item),
                        flatten=flatten,
                        dropna=dropna,
                    )
                )
            else:
                result.append(
                    _process_list(
                        lst=list(item),
                        flatten=flatten,
                        dropna=dropna,
                    )
                )
        elif not dropna or item is not None:
            result.append(item)

    return result


# File: lion_core/libs/data_handlers/_to_list.py
