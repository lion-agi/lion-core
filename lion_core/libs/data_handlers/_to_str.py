import json
from collections.abc import Iterable, Mapping
from typing import Any, TypeVar, overload

from pydantic import BaseModel
from pydantic_core import PydanticUndefined, PydanticUndefinedType

from lion_core.libs.data_handlers._to_dict import to_dict
from lion_core.setting import LN_UNDEFINED, LionUndefinedType

T = TypeVar("T")


@overload
def to_str(
    input_: None | LionUndefinedType | PydanticUndefinedType,
) -> str: ...


@overload
def to_str(input_: str) -> str: ...


@overload
def to_str(input_: BaseModel, **kwargs: Any) -> str: ...


@overload
def to_str(input_: Mapping, **kwargs: Any) -> str: ...


@overload
def to_str(input_: bytes | bytearray) -> str: ...


@overload
def to_str(input_: Iterable, **kwargs: Any) -> str: ...


@overload
def to_str(
    input_: Any,
    *,
    strip_lower: bool = False,
    chars: str | None = None,
    **kwargs: Any,
) -> str: ...


def to_str(
    input_: Any,
    /,
    *,
    strip_lower: bool = False,
    chars: str | None = None,
    **kwargs: Any,
) -> str:
    """
    Convert the input to a string representation.

    This function uses singledispatch to provide type-specific
    implementations for different input types. The base implementation
    handles Any type by converting it to a string using the str() function.

    Args:
        input_: The input to be converted to a string.
        use_model_dump: If True, use model_dump for Pydantic models.
        strip_lower: If True, strip and convert to lowercase.
        chars: Characters to strip from the result.
        **kwargs: Additional arguments for json.dumps.

    Returns:
        String representation of the input.

    Raises:
        ValueError: If conversion fails.

    Examples:
        >>> to_str(123)
        '123'
        >>> to_str("  HELLO  ", strip_lower=True)
        'hello'
        >>> to_str({"a": 1, "b": 2})
        '{"a": 1, "b": 2}'
    """
    try:
        str_ = _dispatch_to_str(input_, **kwargs)
        return _process_string(s=str_, strip_lower=strip_lower, chars=chars)
    except Exception as e:
        raise ValueError(
            f"Could not convert input of type <{type(input_).__name__}> to "
            "string"
        ) from e


def _pydantic_to_str(input_: BaseModel, /, **kwargs: Any) -> str:

    if hasattr(input_, "to_dict"):
        input_ = input_.to_dict()
    else:
        input_ = input_.model_dump()

    return json.dumps(input_, **kwargs)


def _dict_to_str(input_: Mapping, /, **kwargs: Any) -> str:
    input_ = dict(input_)
    return json.dumps(input_, **kwargs)


def _byte_to_str(input_: bytes | bytearray, /) -> str:
    return input_.decode("utf-8", errors="replace")


def _dispatch_to_str(input_: Any, /, **kwargs: Any) -> str:
    if isinstance(input_, str):
        return input_

    if input_ in [LN_UNDEFINED, PydanticUndefined, None, [], {}]:
        return ""

    if isinstance(input_, BaseModel):
        return _pydantic_to_str(input_, **kwargs)

    if isinstance(input_, Mapping):
        return _dict_to_str(input_, **kwargs)

    if isinstance(input_, (bytes, bytearray)):
        return _byte_to_str(input_)

    if isinstance(input_, Iterable):
        return _iterable_to_str(input_, **kwargs)

    try:
        dict_ = to_dict(input_)
        return _dict_to_str(dict_, **kwargs)
    except Exception:
        return str(object=input_)


def _iterable_to_str(input_: Iterable, /, **kwargs: Any) -> str:
    input_ = list(input_)
    return ", ".join(_dispatch_to_str(item, **kwargs) for item in input_)


def _process_string(s: str, strip_lower: bool, chars: str | None) -> str:
    if s in [LN_UNDEFINED, PydanticUndefined, None, [], {}]:
        return ""

    if strip_lower:
        s = s.lower()
        s = s.strip(chars) if chars is not None else s.strip()
    return s


def strip_lower(
    input_: Any,
    /,
    *,
    chars: str | None = None,
    **kwargs: Any,
) -> str:
    """
    Convert input to stripped and lowercase string representation.

    This function is a convenience wrapper around to_str that always
    applies stripping and lowercasing.

    Args:
        input_: The input to convert to a string.
        use_model_dump: If True, use model_dump for Pydantic models.
        chars: Characters to strip from the result.
        **kwargs: Additional arguments to pass to to_str.

    Returns:
        Stripped and lowercase string representation of the input.

    Raises:
        ValueError: If conversion fails.

    Example:
        >>> strip_lower("  HELLO WORLD  ")
        'hello world'
    """
    return to_str(
        input_,
        strip_lower=True,
        chars=chars,
        **kwargs,
    )


# File: lion_core/libs/data_handlers/_to_str.py
