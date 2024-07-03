from collections.abc import Mapping, Generator, Sequence
from collections import deque
from typing import Type
from ..abc import LionIDError, Record, Ordering, AbstractElement


def get_lion_id(item) -> str:
    """Get the Lion ID of an item."""
    if isinstance(item, Sequence) and len(item) == 1:
        item = item[0]
    if isinstance(item, str) and len(item) == 32:
        return item
    if getattr(item, "ln_id", None) is not None:
        return item.ln_id
    raise LionIDError("Item must contain a lion id.")


def to_list_type(value):
    """
    Convert the provided value to a list.

    This function ensures that the input value is converted to a list,
    regardless of its original type. It handles various types including
    Component, Mapping, Record, tuple, list, set, Generator, and deque.

    Args:
        value: The value to convert to a list.

    Returns:
        list: The converted list.

    Raises:
        TypeError: If the value cannot be converted to a list.
    """
    if isinstance(value, AbstractElement) and not isinstance(value, Record):
        return [value]
    if isinstance(value, (Mapping, Record)):
        return list(value.values())
    if isinstance(value, (tuple, list, set, Generator, deque)):
        return list(value)
    return [value]


def validate_order(value) -> list[str]:
    """
    Validate and convert the order field to a list of strings.

    This function ensures that the input value is a valid order and converts it to a list of strings.
    It handles various input types including string, Ordering, and Element.

    Args:
        value: The value to validate and convert.

    Returns:
        list[str]: The validated and converted order list.

    Raises:
        LionTypeError: If the value contains invalid types.
    """
    if value is None:
        return []
    if isinstance(value, str) and len(value) == 32:
        return [value]
    elif isinstance(value, Ordering):
        return value.order

    elif isinstance(value, AbstractElement):
        return [value.ln_id]

    try:
        return [i for item in to_list_type(value) if (i := get_lion_id(item))]
    except Exception as e:
        raise LionIDError("Must only contain lion ids.") from e


def is_same_dtype(
    input_: list | dict, dtype: Type | None = None, return_dtype=False
) -> bool:
    """
    Checks if all elements in a list or dictionary values are of the same data type.

    Args:
            input_ (list | dict): The input list or dictionary to check.
            dtype (Type | None): The data type to check against. If None, uses the type of the first element.

    Returns:
            bool: True if all elements are of the same type (or if the input is empty), False otherwise.
    """
    if not input_:
        return True

    iterable = input_.values() if isinstance(input_, dict) else input_
    first_element_type = type(next(iter(iterable), None))

    dtype = dtype or first_element_type

    a = all(isinstance(element, dtype) for element in iterable)
    return a, dtype if return_dtype else a
