from collections.abc import Callable, Sequence
from typing import Any, Literal, TypedDict

from lion_core.libs.algorithms.jaro_distance import jaro_winkler_similarity

ScoreFunc = Callable[[str, str], float]
HandleUnmatched = Literal["ignore", "raise", "remove", "fill", "force"]


class KeysDict(TypedDict, total=False):
    """TypedDict for keys dictionary."""

    key: Any  # Represents any key-type pair


def validate_keys(
    d_: dict[str, Any],
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
    Force-validate keys in a dictionary based on expected keys.

    Matches keys in the provided dictionary with expected keys, correcting
    mismatches using a similarity score function. Supports various modes
    for handling unmatched keys.

    Args:
        dict_: The dictionary to validate and correct keys for.
        keys: List of expected keys or dictionary mapping keys to types.
        score_func: Function returning similarity score (0-1) for two
            strings. Defaults to Jaro-Winkler similarity.
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
        A new dictionary with validated and corrected keys.

    Raises:
        ValueError: If handle_unmatched is "raise" and unmatched keys
            exist, or if strict is True and expected keys are missing.
    """
    fields_set = set(keys) if isinstance(keys, list) else set(keys.keys())

    if strict:
        if any(k not in d_ for k in fields_set):
            raise ValueError(f"Failed to force_validate_keys for input: {d_}")

    if set(d_.keys()) == fields_set:
        return d_

    if score_func is None:
        score_func = jaro_winkler_similarity

    corrected_out = {}
    used_keys = set()
    old_used_keys = set()

    # TODO: need fixing, this logic is wrong
    if fuzzy_match:
        for k, v in d_.items():
            if k in fields_set:
                corrected_out[k] = v
                fields_set.remove(k)  # Remove the matched key
                used_keys.add(k)
                old_used_keys.add(k)
            else:
                # Calculate scores
                scores = [score_func(k, field) for field in fields_set]

                # Check if scores list is empty
                if not scores:
                    break

                # Find the index of the highest score
                max_score_index = scores.index(max(scores))

                # Select the best match based on the highest score
                best_match = list(fields_set)[max_score_index]

                corrected_out[best_match] = v
                fields_set.remove(best_match)  # Remove the matched key
                used_keys.add(best_match)
                old_used_keys.add(k)

        for k, v in d_.items():
            if k not in old_used_keys:
                corrected_out[k] = v

        if len(used_keys) == len(d_) == fields_set:
            return corrected_out

    if handle_unmatched == "ignore":
        return corrected_out

    if handle_unmatched in ["force", "remove"]:
        for k in set(d_.keys()) - used_keys:
            corrected_out.pop(k, None)
        if handle_unmatched == "remove":
            return corrected_out

    if handle_unmatched in ["force", "fill"]:
        for k in fields_set - used_keys:
            if fill_mapping:
                corrected_out[k] = fill_mapping.get(k, fill_value)
            else:
                corrected_out[k] = fill_value
        if handle_unmatched == "fill":
            return corrected_out

    if handle_unmatched == "force":
        return corrected_out

    raise ValueError(f"Failed to force_validate_keys for input: {d_}")


# File: lion_core/libs/parsers/_force_validate_keys.py
