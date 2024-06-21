"""
Enhanced utilities for JSON parsing, validation, and manipulation.

This module provides a set of tools for handling JSON data, including
fuzzy parsing, key validation, and flexible mapping operations.
"""

import json
from typing import Any, Callable, Dict, List, Optional, Union

import numpy as np

from .string_utility import jaro_winkler_similarity


class JSONUtils:
    @staticmethod
    def fuzzy_parse_json(str_to_parse: str) -> Dict[str, Any]:
        """
        Attempt to parse a JSON string, applying fixes for common issues.

        Args:
            str_to_parse: The JSON string to parse.

        Returns:
            A dictionary representing the parsed JSON.

        Raises:
            ValueError: If parsing fails after all fixing attempts.
        """
        try:
            return json.loads(str_to_parse)
        except json.JSONDecodeError:
            fixed_str = JSONUtils.fix_json_string(str_to_parse)
            try:
                return json.loads(fixed_str)
            except json.JSONDecodeError:
                try:
                    fixed_str = fixed_str.replace("'", '"')
                    return json.loads(fixed_str)
                except json.JSONDecodeError as e:
                    raise ValueError(
                        f"Failed to parse JSON after fixing attempts: {e}"
                    ) from e

    @staticmethod
    def fix_json_string(str_to_parse: str) -> str:
        """
        Fix a JSON string by ensuring all brackets are properly closed.

        Args:
            str_to_parse: The JSON string to fix.

        Returns:
            The fixed JSON string.

        Raises:
            ValueError: If there are mismatched or extra closing brackets.
        """
        brackets = {"{": "}", "[": "]"}
        open_brackets = []

        for char in str_to_parse:
            if char in brackets:
                open_brackets.append(brackets[char])
            elif char in brackets.values():
                if not open_brackets or open_brackets[-1] != char:
                    raise ValueError("Mismatched or extra closing bracket found.")
                open_brackets.pop()

        return str_to_parse + "".join(reversed(open_brackets))

    @staticmethod
    def force_validate_mapping(
        dict_: Union[Dict[str, Any], str],
        keys: Union[Dict[str, Any], List[str]],
        score_func: Optional[Callable[[str, str], float]] = None,
        fuzzy_match: bool = True,
        handle_unmatched: str = "ignore",
        fill_value: Any = None,
        fill_mapping: Optional[Dict[str, Any]] = None,
        strict: bool = False,
    ) -> Dict[str, Any]:
        """
        Force-validate a mapping against a set of expected keys.

        Args:
            dict_: The dictionary or JSON string to validate.
            keys: Expected keys or schema.
            score_func: Function to calculate similarity between keys.
            fuzzy_match: Whether to use fuzzy matching for keys.
            handle_unmatched: Strategy for unmatched keys.
            fill_value: Default value for missing keys.
            fill_mapping: Mapping of fill values for specific keys.
            strict: Whether to raise an error on missing keys.

        Returns:
            A dictionary with validated and possibly corrected keys.

        Raises:
            ValueError: If validation fails or input is invalid.
        """
        if isinstance(dict_, str):
            dict_ = JSONUtils.fuzzy_parse_json(dict_)

        if not isinstance(dict_, dict):
            raise ValueError(f"Invalid input type: {type(dict_)}")

        try:
            return JSONUtils.force_validate_keys(
                dict_=dict_,
                keys=keys,
                score_func=score_func,
                handle_unmatched=handle_unmatched,
                fill_value=fill_value,
                fill_mapping=fill_mapping,
                strict=strict,
                fuzzy_match=fuzzy_match,
            )
        except Exception as e:
            raise ValueError(f"Failed to validate dict: {dict_}") from e

    @staticmethod
    def force_validate_keys(
        dict_: Dict[str, Any],
        keys: Union[Dict[str, Any], List[str]],
        score_func: Optional[Callable[[str, str], float]] = None,
        fuzzy_match: bool = True,
        handle_unmatched: str = "ignore",
        fill_value: Any = None,
        fill_mapping: Optional[Dict[str, Any]] = None,
        strict: bool = False,
    ) -> Dict[str, Any]:
        """
        Force-validate keys in a dictionary based on expected keys.

        Args:
            dict_: The dictionary to validate.
            keys: Expected keys or schema.
            score_func: Function to calculate similarity between keys.
            fuzzy_match: Whether to use fuzzy matching for keys.
            handle_unmatched: Strategy for unmatched keys.
            fill_value: Default value for missing keys.
            fill_mapping: Mapping of fill values for specific keys.
            strict: Whether to raise an error on missing keys.

        Returns:
            A dictionary with validated and possibly corrected keys.

        Raises:
            ValueError: If validation fails in strict mode.
        """
        fields_set = set(keys) if isinstance(keys, list) else set(keys.keys())

        if strict and any(k not in dict_ for k in fields_set):
            raise ValueError(f"Missing required keys in: {dict_}")

        if set(dict_.keys()) == fields_set:
            return dict_

        score_func = score_func or jaro_winkler_similarity
        corrected_out = {}
        used_keys = set()
        old_used_keys = set()

        if fuzzy_match:
            for k, v in dict_.items():
                if k in fields_set:
                    corrected_out[k] = v
                    fields_set.remove(k)
                    used_keys.add(k)
                    old_used_keys.add(k)
                else:
                    scores = np.array([score_func(k, field) for field in fields_set])
                    if len(scores) == 0:
                        break
                    best_match = list(fields_set)[np.argmax(scores)]
                    corrected_out[best_match] = v
                    fields_set.remove(best_match)
                    used_keys.add(best_match)
                    old_used_keys.add(k)

            for k, v in dict_.items():
                if k not in old_used_keys:
                    corrected_out[k] = v

        if handle_unmatched == "ignore":
            return corrected_out

        if handle_unmatched in ["force", "remove"]:
            for k in set(dict_.keys()) - used_keys:
                corrected_out.pop(k, None)
            if handle_unmatched == "remove":
                return corrected_out

        if handle_unmatched in ["force", "fill"]:
            for k in fields_set - used_keys:
                corrected_out[k] = (fill_mapping or {}).get(k, fill_value)
            if handle_unmatched == "fill":
                return corrected_out

        if handle_unmatched == "force":
            return corrected_out

        raise ValueError(f"Failed to validate keys for: {dict_}")
