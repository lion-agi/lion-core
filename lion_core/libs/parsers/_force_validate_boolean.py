"""Provide utility for forcefully validating and converting inputs to boolean."""

from typing import Any

from lion_core.libs.data_handlers import strip_lower


def force_validate_boolean(x: Any) -> bool:
    """
    Forcefully validate and convert the input into a boolean value.

    This function attempts to convert various input types to a boolean value.
    It recognizes common string representations of true and false, as well
    as numeric values.

    Args:
        x: The input to be converted to boolean.

    Returns:
        The boolean representation of the input.

    Raises:
        ValueError: If the input cannot be converted to a boolean value.

    Examples:
        >>> force_validate_boolean("true")
        True
        >>> force_validate_boolean("false")
        False
        >>> force_validate_boolean("yes")
        True
        >>> force_validate_boolean("no")
        False
        >>> force_validate_boolean(True)
        True
        >>> force_validate_boolean("1")
        True
        >>> force_validate_boolean("0")
        False
    """
    if isinstance(x, bool):
        return x

    if strip_lower(x) in ["true", "1", "correct", "yes"]:
        return True

    elif strip_lower(x) in ["false", "0", "incorrect", "no", "none", "n/a"]:
        return False

    raise ValueError(f"Failed to convert {x} into a boolean value")


# File: lion_core/libs/parsers/_force_validate_boolean.py
