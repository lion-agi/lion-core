import unittest
from lion_core.libs.algorithms.jaro_distance import (
    jaro_distance,
    jaro_winkler_similarity,
)


class TestJaroDistanceFunction(unittest.TestCase):

    def test_jaro_distance_exact_match(self):
        self.assertAlmostEqual(jaro_distance("string", "string"), 1.0, places=5)

    def test_jaro_distance_completely_different(self):
        self.assertAlmostEqual(jaro_distance("abc", "xyz"), 0.0, places=5)

    def test_jaro_distance_partial_match(self):
        self.assertAlmostEqual(jaro_distance("dwayne", "duane"), 0.8222, places=4)

    def test_jaro_distance_empty_strings(self):
        self.assertAlmostEqual(jaro_distance("", ""), 1.0, places=5)

    def test_jaro_distance_one_empty_string(self):
        self.assertAlmostEqual(jaro_distance("abc", ""), 0.0, places=5)
        self.assertAlmostEqual(jaro_distance("", "xyz"), 0.0, places=5)

    def test_jaro_distance_numeric_strings(self):
        self.assertAlmostEqual(jaro_distance("123456", "123"), 0.8333, places=4)


class TestJaroWinklerSimilarityFunction(unittest.TestCase):

    def test_jaro_winkler_similarity_exact_match(self):
        self.assertAlmostEqual(
            jaro_winkler_similarity("string", "string"), 1.0, places=5
        )

    def test_jaro_winkler_similarity_completely_different(self):
        self.assertAlmostEqual(jaro_winkler_similarity("abc", "xyz"), 0.0, places=5)

    def test_jaro_winkler_similarity_partial_match(self):
        self.assertAlmostEqual(
            jaro_winkler_similarity("dwayne", "duane"), 0.8400, places=4
        )

    def test_jaro_winkler_similarity_empty_strings(self):
        self.assertAlmostEqual(jaro_winkler_similarity("", ""), 1.0, places=5)

    def test_jaro_winkler_similarity_one_empty_string(self):
        self.assertAlmostEqual(jaro_winkler_similarity("abc", ""), 0.0, places=5)
        self.assertAlmostEqual(jaro_winkler_similarity("", "xyz"), 0.0, places=5)

    def test_jaro_winkler_similarity_numeric_strings(self):
        self.assertAlmostEqual(
            jaro_winkler_similarity("123456", "123"), 0.8833, places=4
        )

    def test_jaro_winkler_similarity_scaling_factor(self):
        self.assertAlmostEqual(
            jaro_winkler_similarity("dwayne", "duane", scaling=0.2), 0.8578, places=4
        )


if __name__ == "__main__":
    unittest.main()
