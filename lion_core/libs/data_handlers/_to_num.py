"""
Module for converting various input types into numeric values.

Provides functions to convert input data to numeric types (int, float,
or complex), with options for bounding values, specifying numeric type,
and controlling precision.
"""

import re
from typing import Any

# Comprehensive regex to capture decimal numbers, fractions, scientific notation,
# and complex numbers
number_regex = re.compile(
    r"[-+]?\d+\.\d+|"  # Decimal numbers with optional sign
    r"[-+]?\d+/\d+|"  # Fractions
    r"[-+]?\d+\.\d*[eE][-+]?\d+|"  # Scientific notation with decimal point
    r"[-+]?\d+[eE][-+]?\d+|"  # Scientific notation without decimal point
    r"[-+]?\d+\+\d+j|"  # Complex numbers with positive imaginary part
    r"[-+]?\d+-\d+j|"  # Complex numbers with negative imaginary part
    r"[-+]?\d+j|"  # Pure imaginary numbers
    r"[-+]?\d+"  # Integers with optional sign
)

# Mapping of string types to Python types
_type_map = {
    "int": int,
    "float": float,
    "complex": complex,
}


def to_num(
    input_: Any,
    /,
    *,
    upper_bound: int | float | None = None,
    lower_bound: int | float | None = None,
    num_type: type[int | float | complex] | str = "float",
    precision: int | None = None,
    num_count: int = 1,
) -> int | float | complex | list[int | float | complex]:
    """
    Convert an input to a numeric type (int, float, or complex).

    Args:
        input_: The input to convert to a number.
        upper_bound: The upper bound for the number. Raises ValueError if
            the number exceeds this bound.
        lower_bound: The lower bound for the number. Raises ValueError if
            the number is below this bound.
        num_type: The type of the number (int, float, or complex).
        precision: The number of decimal places to round to if num_type is float.
        num_count: The number of numeric values to return.

    Returns:
        The converted number or list of numbers.

    Raises:
        ValueError: If no numeric value is found in the input or if the
            number is out of the specified bounds.
        TypeError: If the input is a list.

    Examples:
        >>> to_num("42")
        42.0
        >>> to_num("3.14", num_type=float)
        3.14
        >>> to_num("2/3", num_type=float)
        0.6666666666666666
    """
    if isinstance(input_, list):
        raise TypeError("Input cannot be a list.")

    str_ = str(input_)
    if str_.startswith(("0x", "0b")):
        raise ValueError("Hexadecimal and binary formats are not supported.")

    # Map string types to actual Python types
    if isinstance(num_type, str):
        if num_type not in _type_map:
            raise ValueError(f"Invalid number type string: {num_type}")
        num_type = _type_map[num_type]

    return str_to_num(str_, upper_bound, lower_bound, num_type, precision, num_count)


def str_to_num(
    input_: str,
    upper_bound: float | None = None,
    lower_bound: float | None = None,
    num_type: type[int | float | complex] = float,
    precision: int | None = None,
    num_count: int = 1,
) -> int | float | complex | list[int | float | complex]:
    """
    Convert a string to a numeric type (int, float, or complex).

    Args:
        input_: The input string to convert to a number.
        upper_bound: The upper bound for the number. Raises ValueError if
            the number exceeds this bound.
        lower_bound: The lower bound for the number. Raises ValueError if
            the number is below this bound.
        num_type: The type of the number (int, float, or complex).
        precision: The number of decimal places to round to if num_type is float.
        num_count: The number of numeric values to return.

    Returns:
        The converted number or list of numbers.

    Raises:
        ValueError: If no numeric value is found in the input or if the
            number is out of the specified bounds.

    Examples:
        >>> str_to_num("42")
        42.0
        >>> str_to_num("3.14", num_type=float)
        3.14
        >>> str_to_num("2/3", num_type=float)
        0.6666666666666666
    """
    number_strs = _extract_numbers(input_)
    if not number_strs:
        raise ValueError(f"No numeric values found in the string: {input_}")

    numbers = [_convert_to_num(num_str, num_type, precision) for num_str in number_strs]

    for number in numbers:
        if isinstance(number, (int, float, complex)):
            if upper_bound is not None and number > upper_bound:
                raise ValueError(
                    f"Number {number} is greater than the upper bound of "
                    f"{upper_bound}."
                )
            if lower_bound is not None and number < lower_bound:
                raise ValueError(
                    f"Number {number} is less than the lower bound of "
                    f"{lower_bound}."
                )

    return numbers[0] if num_count == 1 else numbers[:num_count]


def _extract_numbers(input_: str) -> list[str]:
    """
    Extract all numeric values from a string.

    Args:
        input_: The input string to search for numeric values.

    Returns:
        The list of numeric values found in the string.

    Examples:
        >>> _extract_numbers("42 and 3.14 and 2/3")
        ['42', '3.14', '2/3']
    """
    return number_regex.findall(input_)


def _convert_to_num(
    number_str: str,
    num_type: type[int | float | complex] = float,
    precision: int | None = None,
) -> int | float | complex:
    """
    Convert a numeric string to a specified numeric type.

    Args:
        number_str: The numeric string to convert.
        num_type: The type to convert the string to (int, float, or complex).
        precision: The number of decimal places to round to if num_type is float.

    Returns:
        The converted number.

    Raises:
        ValueError: If the specified number type is invalid.

    Examples:
        >>> _convert_to_num('42', int)
        42
        >>> _convert_to_num('3.14', float)
        3.14
        >>> _convert_to_num('2/3', float)
        0.6666666666666666
    """
    if "/" in number_str:
        numerator, denominator = map(float, number_str.split("/"))
        number = numerator / denominator
    elif "j" in number_str:
        number = complex(number_str)
    else:
        number = float(number_str)

    if num_type is int:
        return int(number)
    elif num_type is float:
        return round(number, precision) if precision is not None else number
    elif num_type is complex:
        return number
    else:
        raise ValueError(f"Invalid number type: {num_type}")


# Path: lion_core/libs/data_handlers/_to_num.py
