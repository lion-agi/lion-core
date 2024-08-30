from collections import deque
from collections.abc import Mapping, Sequence
from typing import Any, Literal


def flatten(
    nested_structure: Any,
    /,
    *,
    parent_key: tuple = (),
    sep: str = "|",
    dynamic: bool = False,
    coerce_sequence: bool | Literal["dict", "list"] = False,
    coerce_keys: bool = True,
    max_depth: int | None = None,
) -> dict[tuple | str, Any] | None:

    if coerce_keys and coerce_sequence == "list":
        raise ValueError(
            "coerce_sequence cannot be 'list' when coerce_keys is True"
        )

    if dynamic and coerce_sequence:
        match coerce_sequence:
            case "list" | True:
                coerce_sequence_to_list = True
                coerce_sequence_to_dict = False
            case "dict":
                coerce_sequence_to_list = False
                coerce_sequence_to_dict = True

    else:
        coerce_sequence_to_list = False
        coerce_sequence_to_dict = False

    return _flatten_iterative(
        obj=nested_structure,
        parent_key=parent_key,
        sep=sep,
        coerce_keys=coerce_keys,
        dynamic=dynamic,
        coerce_sequence_to_list=coerce_sequence_to_list,
        coerce_sequence_to_dict=coerce_sequence_to_dict,
        max_depth=max_depth,
    )


def _flatten_iterative(
    obj: Any,
    parent_key: tuple,
    sep: str,
    coerce_keys: bool,
    dynamic: bool,
    coerce_sequence_to_list: bool = False,
    coerce_sequence_to_dict: bool = False,
    max_depth: int | None = None,
) -> dict[tuple | str, Any]:
    stack = deque([(obj, parent_key, 0)])
    result = {}

    while stack:
        current_obj, current_key, depth = stack.pop()

        if max_depth is not None and depth >= max_depth:
            result[_format_key(current_key, sep, coerce_keys)] = current_obj
            continue

        if isinstance(current_obj, Mapping):
            for k, v in current_obj.items():
                new_key = current_key + (k,)
                if (
                    v
                    and isinstance(v, (Mapping, Sequence))
                    and not isinstance(v, (str, bytes, bytearray))
                ):
                    stack.appendleft((v, new_key, depth + 1))
                else:
                    result[_format_key(new_key, sep, coerce_keys)] = v

        elif (
            dynamic
            and isinstance(current_obj, Sequence)
            and not isinstance(current_obj, (str, bytes, bytearray))
        ):
            if coerce_sequence_to_dict:
                dict_obj = {str(i): v for i, v in enumerate(current_obj)}
                for k, v in dict_obj.items():
                    new_key = current_key + (k,)
                    stack.appendleft((v, new_key, depth + 1))
            elif coerce_sequence_to_list:
                for i, v in enumerate(current_obj):
                    new_key = current_key + (i,)
                    stack.appendleft((v, new_key, depth + 1))
            else:
                for i, v in enumerate(current_obj):
                    new_key = current_key + (str(i),)
                    stack.appendleft((v, new_key, depth + 1))
        else:
            result[_format_key(current_key, sep, coerce_keys)] = current_obj

    return result


def _format_key(key: tuple, sep: str, coerce_keys: bool, /) -> tuple | str:
    if not key:
        return key
    return sep.join(map(str, key)) if coerce_keys else key


# File: lion_core/libs/data_handlers/_flatten.py
