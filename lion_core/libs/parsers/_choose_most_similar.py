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

from typing import Callable, Sequence

from lion_core.libs.algorithms.jaro_distance import jaro_winkler_similarity


def choose_most_similar(
    word: str,
    correct_words_list: Sequence[str],
    score_func: Callable[[str, str], float] | None = None,
) -> str | None:
    """
    Choose the most similar word from a list of correct words.

    This function compares the input word against a list of correct words
    using a similarity scoring function, and returns the most similar word.

    Args:
        word: The word to compare.
        correct_words_list: The list of correct words to compare against.
        score_func: A function to compute the similarity score between two
            words. Defaults to jaro_winkler_similarity.

    Returns:
        The word from correct_words_list that is most similar to the input
        word based on the highest similarity score, or None if the list is
        empty.
    """
    if correct_words_list is None or len(correct_words_list) == 0:
        return None

    if score_func is None:
        score_func = jaro_winkler_similarity

    scores = [
        score_func(str(word), str(correct_word)) for correct_word in correct_words_list
    ]

    max_score_index = max(enumerate(scores), key=lambda x: x[1])[0]
    return correct_words_list[max_score_index]


# File: lion_core/libs/parsers/_choose_most_similar.py
