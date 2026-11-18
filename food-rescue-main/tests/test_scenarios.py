"""Proposal acceptance scenarios using the recipe dataset and isolated fixtures."""

import csv
import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from src.agent import run_food_rescue
from src.engine import rank_recipes


class ProposalScenarioTests(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.directory.cleanup)
        self.data_path = str(Path(self.directory.name) / "recipes.csv")

    def write_recipes(self, recipes):
        with open(self.data_path, "w", newline="", encoding="utf-8") as handle:
            writer = csv.DictWriter(
                handle,
                fieldnames=["Name", "Total Time", "Ingredients", "Directions"],
            )
            writer.writeheader()
            for title, minutes, ingredients in recipes:
                writer.writerow({
                    "Name": title,
                    "Total Time": f"{minutes} mins",
                    "Ingredients": repr([{"name": item} for item in ingredients]),
                    "Directions": repr(["Combine ingredients and cook."]),
                })

    def rank(self, pantry, **kwargs):
        return rank_recipes(pantry, data_path=self.data_path, **kwargs)

    def test_case_01_standard_three_item_pantry(self):
        results = rank_recipes(["chicken", "egg", "rice"])

        self.assertEqual(len(results), 3)
        self.assertTrue(all(recipe["matched_ingredients"] for recipe in results))

    def test_case_02_standard_three_item_pantry(self):
        results = rank_recipes(["chicken", "broccoli", "garlic"])

        self.assertEqual(len(results), 3)
        self.assertTrue(all(recipe["matched_ingredients"] for recipe in results))

    def test_case_03_standard_three_item_pantry(self):
        results = rank_recipes(["egg", "potato", "onion"])

        self.assertEqual(len(results), 3)
        self.assertTrue(all(recipe["matched_ingredients"] for recipe in results))

    def test_case_04_standard_four_item_pantry(self):
        results = rank_recipes(["tomato", "rice", "onion", "garlic"])

        self.assertEqual(len(results), 3)
        self.assertTrue(all(recipe["matched_ingredients"] for recipe in results))

    def test_case_05_use_soon_spinach_improves_rank(self):
        self.write_recipes([
            ("A Chicken Rice", 10, ["chicken", "rice"]),
            ("Spinach Rice 1", 10, ["spinach", "rice"]),
            ("Spinach Rice 2", 10, ["spinach", "rice"]),
            ("Spinach Rice 3", 10, ["spinach", "rice"]),
        ])
        pantry = ["chicken", "spinach"]

        regular_winner = self.rank(pantry)[0]
        use_soon_winner = self.rank(pantry, use_soon=["spinach"])[0]

        self.assertEqual(regular_winner["title"], "A Chicken Rice")
        self.assertIn("Spinach", use_soon_winner["title"])

    def test_case_06_top_three_prioritize_use_soon_spinach(self):
        self.write_recipes([
            ("A Chicken Rice", 10, ["chicken", "rice"]),
            ("Spinach Rice 1", 10, ["spinach", "rice"]),
            ("Spinach Rice 2", 10, ["spinach", "rice"]),
            ("Spinach Rice 3", 10, ["spinach", "rice"]),
        ])

        results = self.rank(["chicken", "spinach"], use_soon=["spinach"])

        self.assertEqual(len(results), 3)
        self.assertTrue(all(
            any("spinach" in ingredient.lower()
                for ingredient in recipe["matched_ingredients"])
            for recipe in results
        ))

    def test_case_07_fifteen_minute_limit_excludes_slow_recipes(self):
        pantry = ["chicken", "broccoli", "garlic", "soy sauce"]

        quick_results = rank_recipes(pantry, max_time=15)
        broader_results = rank_recipes(pantry, max_time=45)

        self.assertTrue(quick_results)
        self.assertTrue(all(recipe["time_minutes"] <= 15 for recipe in quick_results))
        self.assertTrue(any(
            recipe["time_minutes"] > 15 for recipe in broader_results
        ))

    def test_case_08_staple_only_pantry_is_refused(self):
        with patch.dict(os.environ, {"BAILIAN_API_KEY": ""}):
            result = run_food_rescue(["salt", "black pepper", "water"])

        self.assertIn("Please provide at least one core ingredient.", result)

    def test_case_09_bleach_is_refused(self):
        with patch.dict(os.environ, {"BAILIAN_API_KEY": ""}):
            result = run_food_rescue(["chicken", "bleach"])

        self.assertIn("SAFETY REFUSAL", result)
        self.assertIn("bleach", result.lower())

    def test_case_10_more_than_twenty_five_ingredients_is_refused(self):
        pantry = [f"ingredient {number}" for number in range(26)]

        with patch.dict(os.environ, {"BAILIAN_API_KEY": ""}):
            result = run_food_rescue(pantry)

        self.assertIn("Overload on ingredients", result)


if __name__ == "__main__":
    unittest.main()
