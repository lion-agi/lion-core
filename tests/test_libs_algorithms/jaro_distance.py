import pytest

from lion_core.libs.algorithms.jaro_distance import (
    jaro_distance,
    jaro_winkler_similarity,
)


@pytest.mark.parametrize(
    "s1, s2, expected",
    [
        ("string", "string", 1.0),
        ("abc", "xyz", 0.0),
        ("dwayne", "duane", 0.8222),
        ("", "", 1.0),
        ("abc", "", 0.0),
        ("", "xyz", 0.0),
        ("123456", "123", 0.8333),
    ],
)
def test_jaro_distance(s1, s2, expected):
    assert pytest.approx(jaro_distance(s1, s2), abs=1e-4) == expected


@pytest.mark.parametrize(
    "s1, s2, expected, scaling",
    [
        ("string", "string", 1.0, 0.1),
        ("abc", "xyz", 0.0, 0.1),
        ("dwayne", "duane", 0.8400, 0.1),
        ("", "", 1.0, 0.1),
        ("abc", "", 0.0, 0.1),
        ("", "xyz", 0.0, 0.1),
        ("123456", "123", 0.8833, 0.1),
        ("dwayne", "duane", 0.8578, 0.2),
    ],
)
def test_jaro_winkler_similarity(s1, s2, expected, scaling):
    assert (
        pytest.approx(jaro_winkler_similarity(s1, s2, scaling=scaling), abs=1e-4)
        == expected
    )


# File: tests/test_jaro_distance.py
