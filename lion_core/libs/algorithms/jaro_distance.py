"""
Jaro distance and Jaro-Winkler similarity calculation functions.

This module provides functions for calculating the Jaro distance and
Jaro-Winkler similarity between two strings. These measures are useful
for comparing the similarity of short strings, such as names or codes.
"""


def jaro_distance(s: str, t: str) -> float:
    """
    Calculate the Jaro distance between two strings.

    The Jaro distance is a measure of similarity between two strings.
    It ranges from 0 (no similarity) to 1 (exact match).

    Args:
        s: The first string to compare.
        t: The second string to compare.

    Returns:
        The Jaro distance between the two strings.

    Algorithm:
        1. Calculate lengths of both strings. If both are empty, return 1.0.
        2. Determine the match distance as half the length of the longer string
           minus one.
        3. Initialize match flags for both strings.
        4. Identify matches within the match distance.
        5. Count transpositions.
        6. Compute and return the Jaro distance.
    """
    s_len = len(s)
    t_len = len(t)

    # If both strings are empty, they are considered identical
    if s_len == 0 and t_len == 0:
        return 1.0

    # Match distance is the maximum distance within which characters can match
    match_distance = (max(s_len, t_len) // 2) - 1

    # Initialize match flags
    s_matches = [False] * s_len
    t_matches = [False] * t_len

    matches = 0
    transpositions = 0

    # Identify matches
    for i in range(s_len):
        start = max(0, i - match_distance)
        end = min(i + match_distance + 1, t_len)

        for j in range(start, end):
            if t_matches[j]:
                continue
            if s[i] != t[j]:
                continue
            s_matches[i] = t_matches[j] = True
            matches += 1
            break

    # If no matches, return 0.0
    if matches == 0:
        return 0.0

    # Count transpositions
    k = 0
    for i in range(s_len):
        if not s_matches[i]:
            continue
        while not t_matches[k]:
            k += 1
        if s[i] != t[k]:
            transpositions += 1
        k += 1

    transpositions //= 2

    # Compute Jaro distance
    return (
        matches / s_len + matches / t_len + (matches - transpositions) / matches
    ) / 3.0


def jaro_winkler_similarity(s: str, t: str, scaling: float = 0.1) -> float:
    """
    Calculate the Jaro-Winkler similarity between two strings.

    An extension of Jaro distance, giving more weight to common prefixes.

    Args:
        s: The first string to compare.
        t: The second string to compare.
        scaling: The scaling factor for the prefix length. Defaults to 0.1.

    Returns:
        The Jaro-Winkler similarity between the two strings.

    Algorithm:
        1. Calculate the Jaro distance.
        2. Determine the length of the common prefix up to 4 characters.
        3. Adjust the Jaro distance with the prefix scaling factor.
    """
    jaro_sim = jaro_distance(s, t)

    prefix_len = 0

    # Find length of common prefix
    for s_char, t_char in zip(s, t):
        if s_char == t_char:
            prefix_len += 1
        else:
            break
        if prefix_len == 4:
            break

    # Calculate and return Jaro-Winkler similarity
    return jaro_sim + (prefix_len * scaling * (1 - jaro_sim))


# Path: lion_core/libs/algorithms/jaro_distance.py
