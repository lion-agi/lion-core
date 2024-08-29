from collections import deque
from collections.abc import Mapping, Sequence
from typing import Any

from lion_core.libs.data_handlers._to_dict import to_dict
from lion_core.libs.data_handlers._to_list import to_list


def flatten(
    nested_structure: Any,
    /,
    *,
    parent_key: tuple = (),
    sep: str = "|",
    coerce_keys: bool = True,
    dynamic: bool = False,
    coerce_sequence_to_list: bool = False,
    coerce_sequence_to_dict: bool = False,
    max_depth: int | None = None,
    inplace: bool = False,
) -> dict[tuple | str, Any] | None:
    if coerce_sequence_to_list and coerce_sequence_to_dict:
        raise ValueError(
            "coerce_sequence_to_list and coerce_sequence_to_dict cannot both "
            "be True"
        )

    if inplace:
        if not isinstance(nested_structure, dict):
            raise ValueError(
                "Inplace flattening is only supported for dictionaries"
            )
        _flatten_inplace(
            d=nested_structure,
            parent_key=parent_key,
            sep=sep,
            coerce_keys=coerce_keys,
            dynamic=dynamic,
            coerce_sequence_to_list=coerce_sequence_to_list,
            coerce_sequence_to_dict=coerce_sequence_to_dict,
            max_depth=max_depth,
        )
        return None

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
    coerce_sequence_to_list: bool,
    coerce_sequence_to_dict: bool,
    max_depth: int | None,
) -> dict[tuple | str, Any]:
    stack = deque([(obj, parent_key, 0)])
    result = {}
    last_obj = None
    last_key = None

    while stack:
        current_obj, current_key, depth = stack.pop()
        last_obj = current_obj
        last_key = current_key

        if max_depth is not None and depth >= max_depth:
            result[
                _format_key(key=current_key, sep=sep, coerce_keys=coerce_keys)
            ] = current_obj
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
                    result[
                        _format_key(
                            key=new_key, sep=sep, coerce_keys=coerce_keys
                        )
                    ] = v

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
                    new_key = current_key + (str(i),)
                    stack.appendleft((v, new_key, depth + 1))
            else:
                for i, v in enumerate(current_obj):
                    new_key = current_key + (str(i),)
                    stack.appendleft((v, new_key, depth + 1))
        else:
            result[
                _format_key(key=current_key, sep=sep, coerce_keys=coerce_keys)
            ] = current_obj

    if last_obj == {} and last_key:
        result[_format_key(key=last_key, sep=sep, coerce_keys=coerce_keys)] = (
            last_obj
        )
    return result


def _format_key(key: tuple, sep: str, coerce_keys: bool) -> tuple | str:
    if not key:
        return key
    return sep.join(map(str, key)) if coerce_keys else key


def _flatten_inplace(
    d: dict,
    parent_key: tuple,
    sep: str,
    coerce_keys: bool,
    dynamic: bool,
    coerce_sequence_to_list: bool,
    coerce_sequence_to_dict: bool,
    max_depth: int | None,
) -> None:
    stack = deque([(d, parent_key, 0)])

    while stack:
        current_dict, current_key, depth = stack.pop()

        if max_depth is not None and depth >= max_depth:
            continue

        for k in list(current_dict.keys()):
            v = current_dict[k]
            new_key = current_key + (k,)

            if isinstance(v, dict):
                stack.appendleft((v, new_key, depth + 1))
                del current_dict[k]
            elif (
                dynamic
                and isinstance(v, Sequence)
                and not isinstance(v, (str, bytes, bytearray))
            ):
                if coerce_sequence_to_dict:
                    dict_obj = to_dict(v)
                    stack.appendleft((dict_obj, new_key, depth + 1))
                elif coerce_sequence_to_list:
                    list_obj = to_list(v)
                    for i, item in enumerate(list_obj):
                        item_key = new_key + (str(i),)
                        current_dict[
                            _format_key(
                                key=item_key, sep=sep, coerce_keys=coerce_keys
                            )
                        ] = item
                else:
                    for i, item in enumerate(v):
                        item_key = new_key + (str(i),)
                        current_dict[
                            _format_key(
                                key=item_key, sep=sep, coerce_keys=coerce_keys
                            )
                        ] = item
                del current_dict[k]
            elif coerce_keys:
                current_dict[
                    _format_key(key=new_key, sep=sep, coerce_keys=coerce_keys)
                ] = current_dict.pop(k)

        if current_dict is not d:
            for k, v in current_dict.items():
                d[k] = v


# File: lion_core/libs/data_handlers/_flatten.py
