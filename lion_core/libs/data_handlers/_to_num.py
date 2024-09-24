import re
from typing import Any, Literal

# Comprehensive regex to capture decimal numbers, fractions, scientific
# notation and complex numbers
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

NUM_TYPES = type[int | float | complex] | Literal["int", "float", "complex"]


def to_num(
    input_: Any,
    /,
    *,
    upper_bound: int | float | None = None,
    lower_bound: int | float | None = None,
    num_type: NUM_TYPES = float,
    precision: int | None = None,
    num_count: int = 1,
) -> int | float | complex | list[int | float | complex]:
    """Convert input to numeric type(s) with various options.

    Extracts and converts numeric values from the input, supporting int,
    float, and complex types, as well as fractions and percentages.

    Args:
        input_: The input to convert to number(s).
        upper_bound: Maximum allowed value (inclusive).
        lower_bound: Minimum allowed value (inclusive).
        num_type: Target numeric type ('int', 'float', 'complex' or their
            type objects).
        precision: Number of decimal places for rounding (float only).
        num_count: Number of numeric values to extract and return.

    Returns:
        int | float | complex | list[int | float | complex]: Converted
        number(s). Returns a single value if num_count=1, else a list.

    Raises:
        ValueError: If no valid numeric value found, value out of bounds,
            or invalid num_type.
        TypeError: If input is a list.

    Examples:
        >>> to_num("42")
        42.0
        >>> to_num("3.14", num_type=int)
        3
        >>> to_num("50%", num_type=float)
        0.5
        >>> to_num("1+2j", num_type=complex)
        (1+2j)
        >>> to_num("10, 20, 30", num_count=3)
        [10.0, 20.0, 30.0]
    """
    if isinstance(input_, list):
        raise TypeError("The value input for `to_num` cannot be of type list")

    if isinstance(input_, bool):
        return float(input_)

    str_ = str(input_)
    if str_.startswith(("0x", "0b")):
        raise ValueError(
            "`to_num` does not support hexadecimal or binary formats."
        )

    # Map string types to actual Python types
    if isinstance(num_type, str):
        if num_type not in _type_map:
            raise ValueError(
                f"Invalid number type string: <{num_type}>. It must be one "
                "of 'int', 'float', or 'complex'."
            )
        num_type = _type_map[num_type]

    return _str_to_num(
        input_=str_,
        upper_bound=upper_bound,
        lower_bound=lower_bound,
        num_type=num_type,
        precision=precision,
        num_count=num_count,
    )


def _str_to_num(
    input_: str,
    upper_bound: float | None = None,
    lower_bound: float | None = None,
    num_type: NUM_TYPES = float,
    precision: int | None = None,
    num_count: int = 1,
) -> int | float | complex | list[int | float | complex]:
    number_strs = _extract_numbers(input_)
    if not number_strs:
        raise ValueError(f"No numeric values found in the string: {input_}")

    numbers = [
        _convert_to_num(num_str, num_type, precision)
        for num_str in number_strs[:num_count]
    ]

    for number in numbers:
        if isinstance(number, (int, float)):
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

    return numbers[0] if num_count == 1 else numbers


def _extract_numbers(input_: str) -> list[str]:
    # Add support for inf, -inf, nan, and percentage
    special_numbers = r"(?:inf|-inf|nan)"
    percentage = r"[-+]?\d+(?:\.\d*)?%"

    full_pattern = r"|".join(
        [number_regex.pattern, special_numbers, percentage]
    )
    return re.findall(full_pattern, input_, re.IGNORECASE)


def _convert_to_num(
    number_str: str,
    num_type: type[int | float | complex] = float,
    precision: int | None = None,
) -> int | float | complex:
    number_str = number_str.strip().lower()

    if number_str in ("inf", "+inf"):
        return float("inf")
    elif number_str == "-inf":
        return float("-inf")
    elif number_str == "nan":
        return float("nan")
    elif number_str.endswith("%"):
        number = float(number_str[:-1]) / 100
    elif "/" in number_str:
        numerator, denominator = map(float, number_str.split("/"))
        number = numerator / denominator
    elif "j" in number_str:
        number = complex(number_str)
    elif "e" in number_str.lower():
        number = float(number_str)
    else:
        number = float(number_str)

    if num_type is int:
        return int(number)
    elif num_type is float:
        return round(number, precision) if precision is not None else number
    elif num_type is complex:
        return complex(number)
    else:
        raise ValueError(f"Invalid number type: {num_type}")


# Path: lion_core/libs/data_handlers/_to_num.py
