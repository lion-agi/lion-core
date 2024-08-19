import json
from typing import Any
from collections.abc import Mapping, Iterable
from functools import singledispatch
from pydantic import BaseModel

from lion_core.libs.data_handlers._to_dict import to_dict
from lion_core.setting import LionUndefined


@singledispatch
def to_str(
    input_: Any,
    /,
    *,
    use_model_dump: bool = True,
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
        result = str(input_)
        return _process_string(result, strip_lower, chars)
    except Exception as e:
        raise ValueError(f"Could not convert to string: {input_}") from e


@to_str.register(str)
def _(input_: str, /, **kwargs: Any) -> str:
    """Handle string inputs."""
    return _process_string(
        input_, kwargs.get("strip_lower", False), kwargs.get("chars")
    )


@to_str.register(bytes)
@to_str.register(bytearray)
def _(input_: bytes | bytearray, /, **kwargs: Any) -> str:
    """Handle bytes and bytearray inputs."""
    return _process_string(
        input_.decode("utf-8", errors="replace"),
        kwargs.get("strip_lower", False),
        kwargs.get("chars"),
    )


@to_str.register(type(None))
@to_str.register(LionUndefined)
def _(_: Any, /, **kwargs: Any) -> str:
    """Handle None and LionUndefined inputs."""
    return ""


@to_str.register(Mapping)
def _(input_: Mapping, /, **kwargs: Any) -> str:
    """Handle Mapping inputs."""
    try:
        dict_input = to_dict(input_, use_model_dump=kwargs.get("use_model_dump", True))
        json_kwargs = {k: v for k, v in kwargs.items() if k != "use_model_dump"}
        result = json.dumps(dict_input, **json_kwargs)
        return _process_string(
            result, kwargs.get("strip_lower", False), kwargs.get("chars")
        )
    except Exception as e:
        raise ValueError(f"Failed to convert Mapping to string: {input_}") from e


@to_str.register(Iterable)
def _(input_: Iterable, /, **kwargs: Any) -> str:
    """Handle Iterable inputs."""
    try:
        input_list = list(input_)
        str_kwargs = {
            k: v for k, v in kwargs.items() if k not in ["strip_lower", "chars"]
        }
        result = ", ".join(to_str(item, **str_kwargs) for item in input_list)
        return _process_string(
            result, kwargs.get("strip_lower", False), kwargs.get("chars")
        )
    except Exception as e:
        raise ValueError(f"Failed to convert Iterable to string: {input_}") from e


@to_str.register(BaseModel)
def _(input_: BaseModel, /, **kwargs: Any) -> str:
    """Handle Pydantic BaseModel inputs."""
    use_model_dump = kwargs.get("use_model_dump", True)
    if use_model_dump:
        return to_str(input_.model_dump(), **kwargs)
    return _process_string(
        str(input_), kwargs.get("strip_lower", False), kwargs.get("chars")
    )


def _process_string(s: str, strip_lower: bool, chars: str | None) -> str:
    """
    Process the resulting string based on strip_lower and chars parameters.

    Args:
        s: The string to process.
        strip_lower: If True, convert to lowercase and strip.
        chars: Characters to strip from the result.

    Returns:
        The processed string.
    """
    if strip_lower:
        s = s.lower()
    return s.strip(chars) if chars is not None else s.strip()


def strip_lower(
    input_: Any,
    /,
    *,
    use_model_dump: bool = True,
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
        input_, strip_lower=True, chars=chars, use_model_dump=use_model_dump, **kwargs
    )


# File: lion_core/libs/data_handlers/_to_str.py
