"""
Copyright 2024 HaiyangLi

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""

from typing import Any, Callable, Sequence, TypedDict, Literal
import re
from lion_core.libs.parsers._md_to_json import md_to_json
from lion_core.libs.parsers._fuzzy_parse_json import fuzzy_parse_json
from lion_core.libs.parsers._validate_keys import validate_keys

ScoreFunc = Callable[[str, str], float]
HandleUnmatched = Literal["ignore", "raise", "remove", "fill", "force"]


class KeysDict(TypedDict, total=False):
    """TypedDict for keys dictionary."""

    key: Any  # Represents any key-type pair


def validate_mapping(
    d_: dict[str, Any] | str,
    keys: Sequence[str] | KeysDict,
    /,
    *,
    score_func: ScoreFunc | None = None,
    fuzzy_match: bool = True,
    handle_unmatched: HandleUnmatched = "ignore",
    fill_value: Any = None,
    fill_mapping: dict[str, Any] | None = None,
    strict: bool = False,
) -> dict[str, Any]:
    """
    Force-validate a mapping against a set of expected keys.

    Takes an input `dict_` and attempts to convert it into a dictionary if
    it's a string. Then validates the dictionary against expected keys
    using the `force_validate_keys` function.

    Args:
        dict_: Input to be validated. Can be a dictionary or a string
            representing a dictionary.
        keys: List of expected keys or dictionary mapping keys to types.
        score_func: Function returning similarity score (0-1) for two
            strings. Defaults to None.
        fuzzy_match: If True, use fuzzy matching for key correction.
        handle_unmatched: Specifies how to handle unmatched keys:
            - "ignore": Keep unmatched keys in output.
            - "raise": Raise ValueError if unmatched keys exist.
            - "remove": Remove unmatched keys from output.
            - "fill": Fill unmatched keys with default value/mapping.
            - "force": Combine "fill" and "remove" behaviors.
        fill_value: Default value for filling unmatched keys.
        fill_mapping: Dictionary mapping unmatched keys to default values.
        strict: If True, raise ValueError if any expected key is missing.

    Returns:
        The validated dictionary.

    Raises:
        ValueError: If the input cannot be converted to a valid dictionary
            or if the validation fails.

    Example:
        >>> input_str = "{'name': 'John', 'age': 30}"
        >>> keys = ['name', 'age', 'city']
        >>> validated_dict = force_validate_mapping(input_str, keys)
        >>> validated_dict
        {'name': 'John', 'age': 30, 'city': None}
    """
    out_ = d_

    if isinstance(out_, str):
        out_ = fuzzy_parse_json(d_, surpress=True)
        if not out_:
            out_ = md_to_json(d_, surpress=True)
        if not out_:
            match = re.search(r"```json\n({.*?})\n```", d_, re.DOTALL)
            if match:
                out_ = match.group(1)
                out_ = fuzzy_parse_json(d_, surpress=True)
        if not out_:
            out_ = fuzzy_parse_json(d_.replace("'", '"'), surpress=True)

    if isinstance(out_, dict):
        try:
            return validate_keys(
                out_,
                keys,
                score_func=score_func,
                handle_unmatched=handle_unmatched,
                fill_value=fill_value,
                fill_mapping=fill_mapping,
                strict=strict,
                fuzzy_match=fuzzy_match,
            )
        except Exception as e:
            raise ValueError(f"Failed to force_validate_dict for input: {d_}") from e

    raise ValueError(f"Failed to force_validate_dict for input: {d_}")


# File: lion_core/libs/parsers/_force_validate_mapping.py
