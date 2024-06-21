"""
String Similarity and Fuzzy Matching Module

This module provides various string similarity algorithms and fuzzy matching
methods for text comparison and analysis.

Functions:
    jaro_distance: Calculate the Jaro distance between two strings.
    jaro_winkler_similarity: Calculate the Jaro-Winkler similarity.
    levenshtein_distance: Calculate the Levenshtein distance.
    fuzzy_match: Find the best fuzzy match from a list of candidates.
    string_similarity: Calculate similarity between two strings.

Classes:
    StringMatcher: A class encapsulating various string matching algorithms.
"""

from typing import List, Tuple, Callable, Optional
from difflib import SequenceMatcher
import numpy as np


def jaro_distance(s1: str, s2: str) -> float:
    """
    Calculate the Jaro distance between two strings.

    Args:
        s1 (str): The first string.
        s2 (str): The second string.

    Returns:
        float: The Jaro distance, a value between 0 and 1.
    """
    if not s1 and not s2:
        return 1.0

    if not s1 or not s2:
        return 0.0

    match_distance = max(len(s1), len(s2)) // 2 - 1

    s1_matches = [False] * len(s1)
    s2_matches = [False] * len(s2)

    matches = 0
    transpositions = 0

    for i in range(len(s1)):
        start = max(0, i - match_distance)
        end = min(i + match_distance + 1, len(s2))

        for j in range(start, end):
            if s2_matches[j]:
                continue
            if s1[i] != s2[j]:
                continue
            s1_matches[i] = s2_matches[j] = True
            matches += 1
            break

    if matches == 0:
        return 0.0

    k = 0
    for i in range(len(s1)):
        if not s1_matches[i]:
            continue
        while not s2_matches[k]:
            k += 1
        if s1[i] != s2[k]:
            transpositions += 1
        k += 1

    return ((matches / len(s1) +
             matches / len(s2) +
             (matches - transpositions / 2) / matches) / 3.0)


def jaro_winkler_similarity(s1: str, s2: str, p: float = 0.1) -> float:
    """
    Calculate the Jaro-Winkler similarity between two strings.

    Args:
        s1 (str): The first string.
        s2 (str): The second string.
        p (float): The scaling factor. Default is 0.1.

    Returns:
        float: The Jaro-Winkler similarity, a value between 0 and 1.
    """
    jaro_dist = jaro_distance(s1, s2)

    if jaro_dist > 0.7:
        prefix = 0
        for i in range(min(len(s1), len(s2), 4)):
            if s1[i] == s2[i]:
                prefix += 1
            else:
                break
        jaro_dist += (p * prefix * (1 - jaro_dist))

    return jaro_dist


def levenshtein_distance(s1: str, s2: str) -> int:
    """
    Calculate the Levenshtein distance between two strings.

    Args:
        s1 (str): The first string.
        s2 (str): The second string.

    Returns:
        int: The Levenshtein distance between the two strings.
    """
    if len(s1) < len(s2):
        return levenshtein_distance(s2, s1)

    if len(s2) == 0:
        return len(s1)

    previous_row = range(len(s2) + 1)
    for i, c1 in enumerate(s1):
        current_row = [i + 1]
        for j, c2 in enumerate(s2):
            insertions = previous_row[j + 1] + 1
            deletions = current_row[j] + 1
            substitutions = previous_row[j] + (c1 != c2)
            current_row.append(min(insertions, deletions, substitutions))
        previous_row = current_row

    return previous_row[-1]


def fuzzy_match(query: str, choices: List[str],
                method: Callable[[str, str], float] = jaro_winkler_similarity
                ) -> Tuple[str, float]:
    """
    Find the best fuzzy match for a query from a list of choices.

    Args:
        query (str): The string to match.
        choices (List[str]): A list of strings to match against.
        method (Callable): The similarity method to use. Default is
                           jaro_winkler_similarity.

    Returns:
        Tuple[str, float]: The best match and its similarity score.
    """
    if not choices:
        return ("", 0.0)

    best_match = max(choices, key=lambda x: method(query, x))
    return (best_match, method(query, best_match))


def string_similarity(s1: str, s2: str) -> float:
    """
    Calculate the similarity ratio between two strings using SequenceMatcher.

    Args:
        s1 (str): The first string.
        s2 (str): The second string.

    Returns:
        float: The similarity ratio, a value between 0 and 1.
    """
    return SequenceMatcher(None, s1, s2).ratio()


class StringUtils:

    @staticmethod
    def choose_most_similar(word: str, correct_words_list: List[str], 
                            score_func: Optional[Callable[[str, str], float]] = None) -> Optional[str]:
        """Choose the most similar word from a list of correct words."""
        if not correct_words_list:
            return None

        if score_func is None:
            score_func = jaro_winkler_similarity

        scores = np.array([score_func(str(word), str(correct_word)) 
                           for correct_word in correct_words_list])
        max_score_index = np.argmax(scores)
        return correct_words_list[max_score_index]

    @staticmethod
    def extract_code_blocks(code: str) -> str:
        """Extract code blocks from a string containing Markdown code blocks."""
        code_blocks = []
        lines = code.split("\n")
        inside_code_block = False
        current_block = []

        for line in lines:
            if line.startswith("```"):
                if inside_code_block:
                    code_blocks.append("\n".join(current_block))
                    current_block = []
                    inside_code_block = False
                else:
                    inside_code_block = True
            elif inside_code_block:
                current_block.append(line)

        if current_block:
            code_blocks.append("\n".join(current_block))

        return "\n\n".join(code_blocks)
    
    @staticmethod
    def fuzzy_match(query: str, choices: List[str],
                    method: Callable[[str, str], float] = jaro_winkler_similarity
                    ) -> Tuple[str, float]:
        """Find best fuzzy match for a query from a list of choices."""
        return fuzzy_match(query, choices, method)

    @staticmethod
    def string_similarity(s1: str, s2: str) -> float:
        """Calculate similarity between two strings using SequenceMatcher."""
        return string_similarity(s1, s2)

