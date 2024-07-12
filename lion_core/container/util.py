"""Utility functions for Lion framework data conversion and validation.

Provides:
- to_list_type: Converts various input types to lists.
- validate_order: Ensures valid order representation for framework objects.
- _validate_str_ln_id: Helper for Lion ID string validation.
"""

from collections import deque
from collections.abc import Generator, Mapping
from typing import Any

from lion_core.abc.element import Element
from lion_core.container.base import Collective, Ordering
from lion_core.exceptions import LionIDError
from lion_core.util.sys_util import SysUtil


def is_str_id(item: str) -> bool:
    """Validate if a string is a valid Lion ID.

    Currently supports two formats:
    1. 34-character string starting with 'ln' (current standard)
    2. 32-character string (deprecated, for backward compatibility)

    Args:
        item: String to validate as a Lion ID.

    Returns:
        bool: True if the string is a valid Lion ID, False otherwise.

    Note:
        The 32-character format is deprecated and will be removed in v1.0+.
        Users should migrate to the 34-character format starting with 'ln'.
    """
    return (len(item) == 34 and item.startswith("ln")) or len(item) == 32  # v1.0-


def to_list_type(value: Any) -> list[Any]:
    """Convert input to a list format compatible with Lion framework.

    Handles None, strings, Collectives, Mappings, Elements, and various
    iterable types including generators.

    Args:
        value: Input of any type to be converted.

    Returns:
        A list representation of the input value.
    """
    if value is None:
        return []
    if isinstance(value, str):
        return [value] if is_str_id(value) else []
    if isinstance(value, (Collective, Mapping)):
        return list(value.values())
    if isinstance(value, Element):
        return [value]
    if isinstance(value, (list, tuple, set, deque, Generator)):
        return list(value)
    return [value]


def validate_order(value: Any) -> list[str]:
    """Validate and standardize order representation for Lion framework.

    Converts input to a list of valid Lion IDs. Handles None, strings,
    Orderings, Elements, and iterables of these types.

    Args:
        value: Input to be validated and converted.

    Returns:
        list of strings representing valid Lion IDs.

    Raises:
        LionIDError: If input contains invalid types or Lion IDs.
    """
    if value is None:
        return []
    if isinstance(value, str) and is_str_id(value):
        return [value]
    if isinstance(value, Ordering):
        return value.order
    if isinstance(value, Element):
        return [value.ln_id]

    try:
        result = []
        for item in to_list_type(value):
            if isinstance(item, str) and is_str_id(item):
                result.append(item)
            elif isinstance(item, Element):
                result.append(item.ln_id)
            else:
                id_ = SysUtil.get_lion_id(item)
                if id_:
                    result.append(id_)
        return result
    except Exception as e:
        raise LionIDError("Must only contain valid Lion IDs.") from e


# File: lion_core/container/util.py
