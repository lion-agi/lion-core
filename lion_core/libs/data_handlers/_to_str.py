import json
from collections.abc import Callable, Mapping
from typing import Any, Literal, TypeVar
from xml.etree import ElementTree as ET

from pydantic_core import PydanticUndefined, PydanticUndefinedType

from lion_core.libs.data_handlers._to_dict import to_dict
from lion_core.setting import LN_UNDEFINED, LionUndefinedType

T = TypeVar("T")


def dict_to_xml(data: dict, /, root_tag: str = "root") -> str:

    root = ET.Element(root_tag)

    def convert(dict_obj: dict, parent: Any) -> None:
        for key, val in dict_obj.items():
            if isinstance(val, dict):
                element = ET.SubElement(parent, key)
                convert(dict_obj=val, parent=element)
            else:
                element = ET.SubElement(parent, key)
                element.text = str(object=val)

    convert(dict_obj=data, parent=root)
    return ET.tostring(root, encoding="unicode")


def _serialize_as(
    input_,
    /,
    *,
    serialize_as: Literal["json", "xml"],
    strip_lower: bool = False,
    chars: str | None = None,
    str_type: Literal["json", "xml"] | None = None,
    use_model_dump: bool = False,
    str_parser: Callable[[str], dict[str, Any]] | None = None,
    parser_kwargs: dict = {},
    root_tag: str = "root",
    **kwargs: Any,
) -> str:
    try:
        dict_ = to_dict(
            input_,
            use_model_dump=use_model_dump,
            str_type=str_type,
            suppress=True,
            parser=str_parser,
            **parser_kwargs,
        )
        if any((str_type, chars)):
            str_ = json.dumps(dict_)
            str_ = _process_string(str_, strip_lower=strip_lower, chars=chars)
            dict_ = json.loads(str_)

        if serialize_as == "json":
            return json.dumps(dict_, **kwargs)

        if serialize_as == "xml":

            return dict_to_xml(dict_, root_tag=root_tag)
    except Exception as e:
        raise ValueError(
            f"Failed to serialize input of {type(input_).__name__} "
            f"into <{str_type}>"
        ) from e


def _to_str_type(input_: Any, /) -> str:

    if isinstance(
        input_, type(None) | LionUndefinedType | PydanticUndefinedType
    ):
        return ""

    if isinstance(input_, bytes | bytearray):
        return input_.decode("utf-8", errors="replace")

    if isinstance(input_, str):
        return input_

    if isinstance(input_, Mapping):
        return json.dumps(dict(input_))

    try:
        return str(input_)
    except Exception as e:
        raise ValueError(
            f"Could not convert input of type <{type(input_).__name__}> "
            "to string"
        ) from e


def to_str(
    input_: Any,
    /,
    *,
    strip_lower: bool = False,
    chars: str | None = None,
    str_type: Literal["json", "xml"] | None = None,
    serialize_as: Literal["json", "xml"] | None = None,
    use_model_dump: bool = False,
    str_parser: Callable[[str], dict[str, Any]] | None = None,
    parser_kwargs: dict = {},
    root_tag: str = "root",
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

    if serialize_as:
        return _serialize_as(
            input_,
            serialize_as=serialize_as,
            strip_lower=strip_lower,
            chars=chars,
            str_type=str_type,
            use_model_dump=use_model_dump,
            str_parser=str_parser,
            parser_kwargs=parser_kwargs,
            root_tag=root_tag,
            **kwargs,
        )

    str_ = _to_str_type(input_, **kwargs)
    if any((strip_lower, chars)):
        str_ = _process_string(str_, strip_lower=strip_lower, chars=chars)
    return str_


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
    str_type: Literal["json", "xml"] | None = None,
    serialize_as: Literal["json", "xml"] | None = None,
    use_model_dump: bool = False,
    str_parser: Callable[[str], dict[str, Any]] | None = None,
    parser_kwargs: dict = {},
    root_tag: str = "root",
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
        str_type=str_type,
        serialize_as=serialize_as,
        use_model_dump=use_model_dump,
        str_parser=str_parser,
        parser_kwargs=parser_kwargs,
        root_tag=root_tag,
        **kwargs,
    )


# File: lion_core/libs/data_handlers/_to_str.py
