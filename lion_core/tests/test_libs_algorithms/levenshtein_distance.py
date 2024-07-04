import unittest
from lion_core.libs.algorithms.levenshtein_distance import (
    levenshtein_distance,
)  # Adjust the import according to your module structure


class TestLevenshteinDistanceFunction(unittest.TestCase):

    def test_levenshtein_distance_exact_match(self):
        self.assertEqual(levenshtein_distance("string", "string"), 0)

    def test_levenshtein_distance_completely_different(self):
        self.assertEqual(levenshtein_distance("abc", "xyz"), 3)

    def test_levenshtein_distance_partial_match(self):
        self.assertEqual(levenshtein_distance("kitten", "sitting"), 3)

    def test_levenshtein_distance_empty_strings(self):
        self.assertEqual(levenshtein_distance("", ""), 0)

    def test_levenshtein_distance_one_empty_string(self):
        self.assertEqual(levenshtein_distance("abc", ""), 3)
        self.assertEqual(levenshtein_distance("", "xyz"), 3)

    def test_levenshtein_distance_numeric_strings(self):
        self.assertEqual(levenshtein_distance("123456", "123"), 3)

    def test_levenshtein_distance_case_difference(self):
        self.assertEqual(levenshtein_distance("String", "string"), 1)

    def test_levenshtein_distance_substitution(self):
        self.assertEqual(levenshtein_distance("flaw", "lawn"), 2)

    def test_levenshtein_distance_insertion_deletion(self):
        self.assertEqual(levenshtein_distance("gumbo", "gambol"), 2)


if __name__ == "__main__":
    unittest.main()
