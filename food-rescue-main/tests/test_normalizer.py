"""Input cleaning and integration regression tests."""

import unittest

from src.engine import rank_recipes
from src.normalizer import normalize_ingredient, normalize_pantry


class NormalizerTests(unittest.TestCase):
    def test_proposal_examples_and_quantities(self):
        cases = {
            "1/2 cup fresh diced spinach": "spinach",
            "large brown eggs": "egg",
            "½ cup fresh spinach": "spinach",
            "1½ cups spinach": "spinach",
            "2 (14 ounce) cans diced tomatoes": "tomato",
            "2 tbsp olive oil": "olive oil",
            "3 cloves minced garlic": "garlic",
            "  200 g FRESH mushrooms  ": "mushroom",
            "salt to taste": "salt",
            "1/2": "",
        }
        for raw, expected in cases.items():
            with self.subTest(raw=raw):
                self.assertEqual(normalize_ingredient(raw), expected)

    def test_preserve_meaningful_food_words(self):
        for food in ("brown rice", "brown sugar", "chicken broth",
                     "garlic powder", "pound cake", "asparagus", "couscous",
                     "sweet potato", "bell pepper", "egg white"):
            with self.subTest(food=food):
                self.assertEqual(normalize_ingredient(food), food)

    def test_pantry_deduplicates_and_accepts_single_string(self):
        self.assertEqual(normalize_pantry(["2 eggs", "egg", "", "spinach"]),
                         ["egg", "spinach"])
        self.assertEqual(normalize_pantry("2 eggs"), ["egg"])

    def test_reject_empty_and_staples_with_quantities(self):
        for pantry in ([], None, [""], ["1 cup water", "1 tsp salt"],
                       ["2 tbsp olive oil", "ground black pepper"]):
            with self.subTest(pantry=pantry), self.assertRaises(ValueError):
                normalize_pantry(pantry)

    def test_reject_non_string_instead_of_silent_conversion(self):
        with self.assertRaises(TypeError):
            normalize_pantry([None])

    def test_engine_raw_input_equals_canonical_input(self):
        self.assertEqual(
            rank_recipes(["2 large brown eggs", "1 cup fresh diced spinach"],
                         use_soon=["½ cup fresh spinach"], max_time=30),
            rank_recipes(["egg", "spinach"], use_soon=["spinach"], max_time=30),
        )

    def test_plain_food_does_not_satisfy_derived_product(self):
        # Existing matcher protection must survive the input-cleaning stage.
        from src.engine import _matches
        self.assertFalse(_matches(normalize_ingredient("2 chicken breasts"),
                                  "chicken broth"))
        self.assertFalse(_matches(normalize_ingredient("3 cloves fresh garlic"),
                                  "garlic powder"))


if __name__ == "__main__":
    unittest.main()
