"""
Comprehensive utilities for converting between various data types.

This module provides a set of functions to convert between different data
types, including lists, dictionaries, strings, and numeric values. These
utilities are designed to handle a wide range of input types and provide
flexible options for customization.

Functions:
    to_list: Convert various input types into a list.
    to_dict: Convert various input types into a dictionary.
    to_str: Convert various input types into a string representation.
    to_num: Convert various input types into numeric values.

Each function includes comprehensive error handling, type checking, and
options for customization to suit various use cases.
"""

from typing import Any, Union, List, Dict, Callable, Optional, Type
from collections import abc
import json
import xml.etree.ElementTree as ET
from decimal import Decimal, InvalidOperation
import numpy as np
import pandas as pd


def to_list(
    input_: Any,
    /,
    *,
    flatten: bool = True,
    dropna: bool = True,
    max_depth: Optional[int] = None,
    item_transformer: Optional[Callable[[Any], Any]] = None,
    filter_func: Optional[Callable[[Any], bool]] = None
) -> List[Any]:
    """
    Convert various types of input into a list with enhanced features.

    Args:
        input_: The input to convert to a list.
        flatten: If True, flattens nested lists. Defaults to True.
        dropna: If True, removes None values. Defaults to True.
        max_depth: Maximum depth for flattening. None for no limit.
        item_transformer: Function to transform each item in the list.
        filter_func: Function to filter items in the list.

    Returns:
        The converted list.

    Examples:
        >>> to_list([1, [2, 3], [[4], 5]], max_depth=1)
        [1, [2, 3], [[4], 5]]
        >>> to_list([1, 2, 3], item_transformer=lambda x: x * 2)
        [2, 4, 6]
        >>> to_list([1, None, 2, 3], filter_func=lambda x: x != 2)
        [1, 3]
    """
    def recursive_flatten(item, depth=0):
        if max_depth is not None and depth >= max_depth:
            yield item
            return

        if isinstance(item, (str, bytes, bytearray)) or not isinstance(
            item, abc.Iterable
        ):
            yield item
        else:
            for sub_item in item:
                yield from recursive_flatten(sub_item, depth + 1)

    if input_ is None:
        return []

    if not isinstance(input_, abc.Iterable) or isinstance(
        input_, (str, bytes, bytearray, dict)
    ):
        input_ = [input_]

    result = list(recursive_flatten(input_)) if flatten else list(input_)

    if dropna:
        result = [item for item in result if item is not None]

    if item_transformer:
        result = [item_transformer(item) for item in result]

    if filter_func:
        result = [item for item in result if filter_func(item)]

    return result


def to_dict(
    input_: Any,
    /,
    as_list: bool = True,
    use_model_dump: bool = True,
    str_type: str = "json",
    max_depth: Optional[int] = None,
    key_transformer: Optional[Callable[[str], str]] = None,
    value_transformer: Optional[Callable[[Any], Any]] = None,
    ignore_keys: Optional[List[str]] = None,
    include_keys: Optional[List[str]] = None,
    **kwargs: Any
) -> Union[Dict[str, Any], List[Dict[str, Any]]]:
    """
    Convert various types of input into a dictionary with advanced options.

    Args:
        input_: The input data to convert.
        as_list: If True, converts DataFrame rows to a list of dictionaries.
        use_model_dump: If True, use model_dump method if available.
        str_type: The type of string to convert. Options: "json", "xml".
        max_depth: Maximum depth for nested structures. None for no limit.
        key_transformer: Function to transform dictionary keys.
        value_transformer: Function to transform dictionary values.
        ignore_keys: List of keys to ignore in the resulting dictionary.
        include_keys: List of keys to include in the resulting dictionary.
        **kwargs: Additional arguments to pass to conversion methods.

    Returns:
        The converted dictionary or list of dictionaries.

    Raises:
        ValueError: If the input type is unsupported or conversion fails.
    """
    def recursive_convert(obj, depth=0):
        if max_depth is not None and depth >= max_depth:
            return obj

        if isinstance(obj, dict):
            return {
                key_transformer(k) if key_transformer else k: recursive_convert(
                    v, depth + 1
                )
                for k, v in obj.items()
                if (not ignore_keys or k not in ignore_keys)
                and (not include_keys or k in include_keys)
            }
        elif isinstance(obj, list):
            return [recursive_convert(item, depth + 1) for item in obj]
        elif hasattr(obj, 'to_dict'):
            return recursive_convert(obj.to_dict(), depth + 1)
        elif isinstance(obj, pd.DataFrame):
            return recursive_convert(obj.to_dict('records'), depth + 1)
        elif isinstance(obj, np.ndarray):
            return recursive_convert(obj.tolist(), depth + 1)
        else:
            return value_transformer(obj) if value_transformer else obj

    if isinstance(input_, str):
        if str_type == "json":
            input_ = json.loads(input_)
        elif str_type == "xml":
            input_ = ET.fromstring(input_)
            input_ = _xml_to_dict(input_)
        else:
            raise ValueError(f"Unsupported string type: {str_type}")
    elif isinstance(input_, pd.DataFrame):
        input_ = input_.to_dict('records') if as_list else input_.to_dict()
    elif hasattr(input_, 'model_dump') and use_model_dump:
        input_ = input_.model_dump(**kwargs)
    elif hasattr(input_, 'to_dict'):
        input_ = input_.to_dict(**kwargs)

    return recursive_convert(input_)


def to_str(
    input_: Any,
    /,
    use_model_dump: bool = True,
    strip_lower: bool = False,
    max_depth: Optional[int] = None,
    custom_formatter: Optional[Callable[[Any], str]] = None,
    indent: Optional[int] = None,
    separator: str = ", ",
    date_format: str = "%Y-%m-%d %H:%M:%S",
    nan_str: str = "NaN",
    inf_str: str = "Inf",
    **kwargs: Any,
) -> str:
    """
    Convert the input to a string representation with enhanced features.

    Args:
        input_: The input to be converted to a string.
        use_model_dump: Whether to use a custom model dump function.
        strip_lower: Whether to strip and convert the string to lowercase.
        max_depth: Maximum depth for nested structures. None for no limit.
        custom_formatter: A custom function to format specific types.
        indent: Number of spaces for indentation in JSON output.
        separator: Separator for joining list elements.
        date_format: Format string for datetime objects.
        nan_str: String representation for NaN values.
        inf_str: String representation for Inf values.
        **kwargs: Additional keyword arguments to pass to json.dumps.

    Returns:
        The string representation of the input.

    Raises:
        ValueError: If the input cannot be converted to a string.

    Examples:
        >>> to_str({"key": "value"}, indent=2)
        '{\n  "key": "value"\n}'
        >>> to_str([1, 2, 3], separator=" | ")
        '1 | 2 | 3'
    """
    def recursive_str(obj, depth=0):
        if max_depth is not None and depth >= max_depth:
            return str(obj)

        if custom_formatter:
            custom_result = custom_formatter(obj)
            if custom_result is not None:
                return custom_result

        if isinstance(obj, (str, int, float, bool, type(None))):
            if isinstance(obj, float):
                if np.isnan(obj):
                    return nan_str
                elif np.isinf(obj):
                    return inf_str
            return str(obj)
        elif isinstance(obj, dict):
            return {
                recursive_str(k, depth + 1): recursive_str(v, depth + 1)
                for k, v in obj.items()
            }
        elif isinstance(obj, (list, tuple, set)):
            return [recursive_str(item, depth + 1) for item in obj]
        elif hasattr(obj, 'strftime'):  # datetime objects
            return obj.strftime(date_format)
        elif hasattr(obj, 'to_dict'):  # pandas objects
            return recursive_str(obj.to_dict(), depth + 1)
        elif np.isscalar(obj):  # numpy scalars
            return str(obj)
        elif hasattr(obj, '__dict__'):  # custom objects
            return recursive_str(obj.__dict__, depth + 1)
        else:
            return str(obj)

    result = recursive_str(input_)

    if isinstance(result, dict):
        result = json.dumps(result, indent=indent, default=str, **kwargs)
    elif isinstance(result, list):
        result = separator.join(map(str, result))

    if strip_lower:
        result = result.strip().lower()

    return result


def to_num(
    input_: Any,
    /,
    *,
    upper_bound: Optional[Union[int, float]] = None,
    lower_bound: Optional[Union[int, float]] = None,
    num_type: Union[Type[Union[int, float, complex, Decimal]], str] = float,
    precision: Optional[int] = None,
    num_count: int = 1,
    allow_inf: bool = False,
    allow_nan: bool = False,
    on_error: str = 'raise',
    default: Any = None,
) -> Union[int, float, complex, Decimal, List[Union[int, float, complex, Decimal]]]:
    """
    Convert an input to a numeric type with enhanced features.

    Args:
        input_: The input to convert to a number.
        upper_bound: The upper bound for the number.
        lower_bound: The lower bound for the number.
        num_type: The type of the number ('int', 'float', 'complex', 
                  'decimal', or type object).
        precision: The number of decimal places to round to if num_type
                   is float or Decimal.
        num_count: The number of numeric values to return.
        allow_inf: Whether to allow infinite values.
        allow_nan: Whether to allow NaN values.
        on_error: How to handle errors ('raise', 'return_default', 
                  'coerce_to_nan').
        default: The default value to return if on_error is 'return_default'.

    Returns:
        The converted number or list of numbers.

    Raises:
        ValueError: If numeric conversion fails and on_error is 'raise'.

    Examples:
        >>> to_num("42.5", num_type=int)
        42
        >>> to_num("3.14159", precision=2)
        3.14
        >>> to_num("1e-5", num_type='decimal')
        Decimal('0.00001')
    """
    TYPE_MAP = {
        'int': int,
        'float': float,
        'complex': complex,
        'decimal': Decimal
    }

    if isinstance(num_type, str):
        num_type = TYPE_MAP.get(num_type.lower(), float)

    def convert_single(value):
        try:
            if isinstance(value, str):
                value = value.strip().lower()
                if value in ('inf', '+inf', 'infinity', '+infinity'):
                    return float('inf') if allow_inf else upper_bound
                elif value in ('-inf', '-infinity'):
                    return float('-inf') if allow_inf else lower_bound
                elif value in ('nan', 'null', 'none'):
                    return float('nan') if allow_nan else default

            if num_type == int:
                result = int(float(value))  # handles exponential notation
            elif num_type == Decimal:
                result = Decimal(value)
            else:
                result = num_type(value)

            if precision is not None and num_type in (float, Decimal):
                result = round(result, precision)

            if upper_bound is not None and result > upper_bound:
                result = upper_bound
            if lower_bound is not None and result < lower_bound:
                result = lower_bound

            return result
        except (ValueError, TypeError, InvalidOperation):
            if on_error == 'raise':
                raise ValueError(f"Cannot convert {value} to {num_type.__name__}")
            elif on_error == 'return_default':
                return default
            elif on_error == 'coerce_to_nan':
                return float('nan')

    if isinstance(input_, (list, tuple, np.ndarray, pd.Series)):
        results = [convert_single(x) for x in input_]
        return results if num_count > 1 else results[0]
    else:
        return convert_single(input_)


def _xml_to_dict(element: ET.Element) -> Dict[str, Any]:
    """Helper function to convert XML to dictionary."""
    result = {}
    for child in element:
        child_data = _xml_to_dict(child)
        if child.tag in result:
            if isinstance(result[child.tag], list):
                result[child.tag].append(child_data)
            else:
                result[child.tag] = [result[child.tag], child_data]
        else:
            result[child.tag] = child_data
    if not result and element.text:
        result = element.text.strip()
    return result
