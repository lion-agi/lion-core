"""Provide utility for forcefully validating and converting to boolean."""

from typing import Any


def validate_boolean(x: Any) -> bool:
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

    if str(x).strip().lower() in ["true", "1", "correct", "yes"]:
        return True

    elif str(x).strip().lower() in [
        "false",
        "0",
        "incorrect",
        "no",
        "none",
        "n/a",
    ]:
        return False

    raise ValueError(f"Failed to convert {x} into a boolean value")


# File: lion_core/libs/parsers/_force_validate_boolean.py
