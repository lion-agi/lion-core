from typing import Any

from lion_core.libs.data_handlers._util import get_target_container
from lion_core.setting import LN_UNDEFINED


def nget(
    nested_structure: dict[Any, Any] | list[Any],
    /,
    indices: list[int | str],
    default: Any = LN_UNDEFINED,
) -> Any:
    """Retrieve a value from a nested structure using a list of indices.

    Args:
        nested_structure: The nested structure to retrieve the value from.
        indices: List of indices to navigate through the nested structure.
        default: Value to return if target not found. If not provided,
            raises LookupError.

    Returns:
        Retrieved value or default if provided.

    Raises:
        LookupError: If target not found and no default value provided.

    Example:
        >>> data = {"a": [{"b": 1}, {"c": 2}]}
        >>> nget(data, ["a", 1, "c"])
        2
        >>> nget(data, ["a", 2, "d"], default="Not found")
        'Not found'
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
        elif (
            isinstance(target_container, dict)
            and last_index in target_container
        ):
            return target_container[last_index]
        elif default is not LN_UNDEFINED:
            return default
        else:
            raise LookupError(
                "Target not found and no default value provided."
            )
    except (IndexError, KeyError, TypeError):
        if default is not LN_UNDEFINED:
            return default
        else:
            raise LookupError(
                "Target not found and no default value provided."
            )


# Path: lion_core/libs/data_handlers/_nget.py
