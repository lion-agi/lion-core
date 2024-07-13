"""
Retrieve a value from a nested structure using a list of indices.

This module provides a function to navigate through a nested dictionary or
list based on provided indices and return the value found at the target
location.

Functions:
- nget: Retrieve a value from a nested structure using a list of indices.
"""

from lion_core.libs.data_handlers._util import get_target_container
from typing import Any
from lion_core.util import LN_UNDEFINED


def nget(
    nested_structure: dict[Any, Any] | list[Any],
    indices: list[int | str],
    default: Any = LN_UNDEFINED,
) -> Any:
    """
    Retrieve a value from a nested structure using a list of indices.

    Args:
        nested_structure: The nested structure to retrieve the value from.
        indices: A list of indices to navigate through the nested structure.
        default: The default value to return if the target value is not found.
            If not provided, a LookupError is raised.

    Returns:
        The value retrieved from the nested structure, or the default value
        if provided.

    Raises:
        LookupError: If the target value is not found and no default value
            is provided.
    """
    try:
        target_container = get_target_container(nested_structure, indices[:-1])
        last_index = indices[-1]

        if (
            isinstance(target_container, list)
            and isinstance(last_index, int)
            and last_index < len(target_container)
        ):
            return target_container[last_index]
        elif isinstance(target_container, dict) and last_index in target_container:
            return target_container[last_index]
        elif default is not LN_UNDEFINED:
            return default
        else:
            raise LookupError("Target not found and no default value provided.")
    except (IndexError, KeyError, TypeError):
        if default is not LN_UNDEFINED:
            return default
        else:
            raise LookupError("Target not found and no default value provided.")


# Path: lion_core/libs/data_handlers/_nget.py
