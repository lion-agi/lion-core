import pytest

from lion_core.libs.algorithms.levenshtein_distance import levenshtein_distance


@pytest.mark.parametrize(
    "s1, s2, expected",
    [
        ("string", "string", 0),
        ("abc", "xyz", 3),
        ("kitten", "sitting", 3),
        ("", "", 0),
        ("abc", "", 3),
        ("", "xyz", 3),
        ("123456", "123", 3),
        ("String", "string", 1),
        ("flaw", "lawn", 2),
        ("gumbo", "gambol", 2),
    ],
)
def test_levenshtein_distance(s1, s2, expected):
    assert levenshtein_distance(s1, s2) == expected


# File: tests/test_levenshtein_distance.py
