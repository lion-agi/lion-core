"""
Module for converting various input types into dictionaries.

Provides functions to convert a variety of data structures, including
DataFrames, JSON strings, and XML elements, into dictionaries or lists
of dictionaries. Handles special cases such as replacing NaN values
with None.
"""

from collections.abc import Mapping
import json
from typing import Any, TypeVar

T = TypeVar("T", bound=dict[str, Any] | list[dict[str, Any]])


def to_dict(
    input_: Any,
    /,
    use_model_dump: bool = True,
    str_type: str = "json",
    **kwargs: Any,
) -> T:
    """
    Convert various types of input into a dictionary or list of dictionaries.

    Args:
        input_: The input data to convert.
        use_model_dump: If True, use model_dump method if available.
        str_type: The type of string to convert. Can be "json" or "xml".
        **kwargs: Additional arguments to pass to conversion methods.

    Returns:
        The converted dictionary or list of dictionaries.

    Raises:
        json.JSONDecodeError: If the input string cannot be parsed as JSON.
        ValueError: If the input type is unsupported.
    """
    out = None
    if isinstance(input_, list):
        out = [
            to_dict(
                i,
                use_model_dump=use_model_dump,
                str_type=str_type,
                **kwargs,
            )
            for i in input_
        ]
    else:
        out = _to_dict(
            input_,
            use_model_dump=use_model_dump,
            str_type=str_type,
            **kwargs,
        )

    if out in [[], {}]:
        return {}

    if isinstance(out, list) and len(out) == 1 and isinstance(out[0], dict):
        return out[0]

    return out


def _to_dict(
    input_: Any,
    /,
    use_model_dump: bool = True,
    str_type: str = "json",
    **kwargs: Any,
) -> dict[str, Any]:
    """
    Helper function to convert the input into a dictionary.

    Args:
        input_: The input data to convert.
        use_model_dump: If True, use model_dump method if available.
        str_type: The type of string to convert. Can be "json" or "xml".
        **kwargs: Additional arguments to pass to conversion methods.

    Returns:
        The converted dictionary.

    Raises:
        json.JSONDecodeError: If the input string cannot be parsed as JSON.
        ValueError: If the input type is unsupported.
    """
    if isinstance(input_, dict):
        return input_

    if isinstance(input_, Mapping):
        return dict(input_)

    if isinstance(input_, str):
        a = None
        if str_type == "xml":
            a = xml_to_dict(input_)

        elif str_type == "json":
            a = json.loads(input_, **kwargs)

        if isinstance(a, dict):
            return a
        raise ValueError("Input string cannot be converted into a dictionary.")

    if use_model_dump and hasattr(input_, "model_dump"):
        return input_.model_dump(**kwargs)

    if hasattr(input_, "to_dict"):
        return input_.to_dict(**kwargs)

    if hasattr(input_, "json"):
        return json.loads(input_.json(**kwargs))

    if hasattr(input_, "dict"):
        return input_.dict(**kwargs)

    try:
        return dict(input_)
    except Exception as e:
        raise e


def xml_to_dict(input_: str) -> dict[str, Any]:
    """
    Convert an XML string to a dictionary.

    Args:
        input_: The XML string to convert.

    Returns:
        The dictionary representation of the XML structure.

    Raises:
        ImportError: If xmltodict is not installed.
    """

    from lion_core.sys_util import SysUtil

    SysUtil.check_import("xmltodict")

    import xmltodict

    return xmltodict.parse(input_)


# Path: lion_core/libs/data_handlers/_to_dict.py
