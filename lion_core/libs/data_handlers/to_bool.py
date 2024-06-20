from .to_str import strip_lower


def to_bool(x):
    """
    Forcefully validates and converts the input into a boolean value.

    Args:
        x (Any): The input to be converted to boolean.

    Returns:
        bool: The boolean representation of the input.

    Raises:
        ValueError: If the input cannot be converted to a boolean value.

    Examples:
        >>> to_bool("true")
        True
        >>> to_bool("false")
        False
        >>> to_bool("yes")
        True
        >>> to_bool("no")
        False
        >>> to_bool(True)
        True
        >>> to_bool("1")
        True
        >>> to_bool("0")
        False
    """
    if isinstance(x, bool):
        return x

    if strip_lower(x) in ["true", "1", "correct", "yes"]:
        return True

    elif strip_lower(x) in ["false", "0", "incorrect", "no", "none", "n/a"]:
        return False

    raise ValueError(f"Failed to convert {x} into a boolean value")
