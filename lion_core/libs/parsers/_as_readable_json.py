"""Provide utility for converting various inputs to readable JSON strings."""

from typing import Any
import json
from lion_core.libs.data_handlers import to_dict


def as_readable_json(input_: Any, /) -> str:
    """
    Convert the input to a readable JSON string.

    This function attempts to convert the input to a dictionary and then
    to a formatted JSON string. If conversion to a dictionary fails, it
    returns the string representation of the input.

    Args:
        input_: The input to be converted to a readable JSON string.

    Returns:
        A formatted JSON string if the input can be converted to a
        dictionary, otherwise the string representation of the input.

    Raises:
        ValueError: If the input cannot be converted to a readable dict.
    """
    try:
        dict_ = to_dict(input_)
        return json.dumps(dict_, indent=4) if isinstance(dict_, dict) else str(dict_)
    except Exception as e:
        raise ValueError(f"Could not convert given input to readable dict: {e}") from e


# Path: lion_core/libs/parsers/_as_readable_json.py
