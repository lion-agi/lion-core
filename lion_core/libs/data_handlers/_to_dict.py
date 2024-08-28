import json
from collections.abc import Callable, Mapping, Sequence
from typing import Any, Literal, TypeVar, overload

from pydantic_core import PydanticUndefined, PydanticUndefinedType

from lion_core.setting import LN_UNDEFINED, LionUndefinedType

T = TypeVar("T", bound=dict[str, Any] | list[dict[str, Any]])


@overload
def to_dict(
    input_: None | LionUndefinedType | PydanticUndefinedType, /
) -> dict[str, Any]: ...


@overload
def to_dict(input_: Mapping, /) -> dict[str, Any]: ...


@overload
def to_dict(
    input_: str,
    /,
    *,
    str_type: Literal["json", "xml"] | None = None,
    parser: Callable[[str], dict[str, Any]] | None = None,
    **kwargs: Any,
) -> dict[str, Any] | list[dict[str, Any]]: ...


@overload
def to_dict(
    input_: Sequence,
    /,
    **kwargs: Any,
) -> list[dict[str, Any]] | dict[str, Any]: ...


@overload
def to_dict(
    input_: Any,
    /,
    *,
    use_model_dump: bool = False,
    **kwargs: Any,
) -> dict[str, Any]: ...


def to_dict(
    input_: Any,
    /,
    *,
    use_model_dump: bool = False,
    str_type: Literal["json", "xml"] | None = None,
    parser: Callable[[str], dict[str, Any]] | None = None,
    **kwargs: Any,
) -> T:
    """
    Convert various input types to a dictionary or list of dictionaries.

    Accepted input types and their behaviors:
    1. None or LionUndefined: Returns an empty dictionary {}.
    2. Mapping (dict, OrderedDict, etc.): Returns a dict representation.
    3. Sequence (list, tuple, etc.):
       - Returns a list of converted items.
       - If the sequence contains only one dict, returns that dict.
    4. set: Converts to a list.
    5. str:
       - If empty, returns {}.
       - If str_type is "json", attempts to parse as JSON.
       - If str_type is "xml", attempts to parse as XML.
       - For invalid JSON, returns the original string.
    6. Objects with .model_dump() method (if use_model_dump is True):
       Calls .model_dump() and returns the result.
    7. Objects with .to_dict(), .dict(), or .json() methods:
       Calls the respective method and returns the result.
    8. Objects with .__dict__ attribute: Returns the .__dict__.
    9. Any other object that can be converted to a dict.

    Args:
        input_: The input to be converted.
        use_model_dump: If True, use model_dump method when available.
        str_type: The type of string to parse ("json" or "xml").
        parser: A custom parser function for string inputs.
        **kwargs: Additional keyword arguments for conversion methods.

    Returns:
        A dictionary, list of dictionaries, or list, depending on the input.

    Raises:
        ValueError: If the input cannot be converted to a dictionary.
    """

    return _dispatch_from_dict(
        input_,
        use_model_dump=use_model_dump,
        str_type=str_type,
        parser=parser,
        **kwargs,
    )


def _dispatch_from_dict(
    input_: Any,
    /,
    *,
    use_model_dump: bool = False,
    str_type: Literal["json", "xml"] | None = None,
    parser: Callable[[str], dict[str, Any]] | None = None,
    **kwargs: Any,
) -> T:

    if input_ in [LN_UNDEFINED, PydanticUndefined, None, [], {}]:
        return {}

    if isinstance(input_, Mapping):
        return dict(input_)

    if isinstance(input_, str):
        return _str_to_dict(input_, str_type=str_type, parser=parser, **kwargs)

    if isinstance(input_, Sequence):
        return _sequence_to_dict(input_, **kwargs)

    return _generic_type_to_dict(
        input_, use_model_dump=use_model_dump, **kwargs
    )


def _sequence_to_dict(
    input_: Sequence,
    /,
    **kwargs: Any,
) -> list[dict[str, Any]] | dict[str, Any]:
    """Handle Sequence inputs."""
    if not input_:
        return []
    out = [
        (
            to_dict(item, **kwargs)
            if isinstance(item, Mapping | Sequence)
            and not isinstance(item, str)
            else item
        )
        for item in input_
    ]
    return out[0] if len(out) == 1 and isinstance(out[0], dict) else out


def _str_to_dict(
    input_: str,
    /,
    *,
    str_type: Literal["json", "xml"] | None = "json",
    parser: Callable[[str], dict[str, Any]] | None = None,
    **kwargs: Any,
) -> dict[str, Any] | list[dict[str, Any]]:
    """Handle string inputs."""
    if not input_:
        return {}

    if str_type == "json":
        try:
            return (
                json.loads(input_, **kwargs)
                if parser is None
                else parser(input_, **kwargs)
            )
        except json.JSONDecodeError as e:
            raise ValueError("Failed to parse JSON string") from e

    if str_type == "xml":
        try:
            if parser is None:
                from lion_core.libs.parsers._xml_parser import xml_to_dict

                return xml_to_dict(input_)
            return parser(input_, **kwargs)
        except Exception as e:
            raise ValueError("Failed to parse XML string") from e

    raise ValueError(f"Unsupported string type: {str_type}")


def _generic_type_to_dict(
    input_,
    /,
    *,
    use_model_dump: bool,
    **kwargs: Any,
) -> dict[str, Any]:
    if use_model_dump and hasattr(input_, "model_dump"):
        return input_.model_dump(**kwargs)

    for method in ["to_dict", "dict", "json", "to_json"]:
        if hasattr(input_, method):
            result = getattr(input_, method)(**kwargs)
            return (
                json.loads(result)
                if method == "json" and isinstance(result, str)
                else result
            )

    if hasattr(input_, "__dict__"):
        return input_.__dict__

    try:
        return dict(input_)
    except Exception as e:
        raise ValueError(f"Unable to convert input to dictionary: {e}")


# File: lion_core/libs/data_handlers/_to_dict.py
