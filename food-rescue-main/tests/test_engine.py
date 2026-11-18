"""Deterministic ranking checks; no API key or third-party packages needed."""

import csv
import tempfile
import unittest
from pathlib import Path

from src.engine import match_recipes, rank_recipes


class RankingTests(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.directory.cleanup)
        self.data_path = str(Path(self.directory.name) / "recipes.csv")

    def write_recipes(self, recipes):
        with open(self.data_path, "w", newline="", encoding="utf-8") as handle:
            writer = csv.DictWriter(
                handle, fieldnames=["Name", "Total Time", "Ingredients", "Directions"]
            )
            writer.writeheader()
            for title, minutes, ingredients in recipes:
                writer.writerow({
                    "Name": title,
                    "Total Time": minutes,
                    "Ingredients": repr([{"name": item} for item in ingredients]),
                    "Directions": repr(["Combine ingredients and cook."]),
                })

    def rank(self, pantry, **kwargs):
        return rank_recipes(pantry, data_path=self.data_path, **kwargs)

    def test_top_three_sort_by_score_then_matches_then_title(self):
        self.write_recipes([
            ("Zulu", "10 mins", ["egg", "rice"]),
            ("Bravo", "10 mins", ["egg", "rice"]),
            ("Alpha", "10 mins", ["egg"]),
            ("Partial", "10 mins", ["egg", "tomato"]),
        ])
        result = self.rank(["eggs", "rice"])
        self.assertEqual([r["title"] for r in result], ["Bravo", "Zulu", "Alpha"])
        self.assertEqual(result, self.rank(["eggs", "rice"]))
        self.assertEqual(
            match_recipes(["eggs", "rice"], data_path=self.data_path), result[0]
        )

    def test_hard_time_limit_includes_boundary_excludes_unknown(self):
        self.write_recipes([
            ("Boundary", "15 mins", ["egg"]),
            ("Slow", "16 mins", ["egg"]),
            ("Unknown", "", ["egg"]),
        ])
        self.assertEqual(
            [r["title"] for r in self.rank(["egg"], max_time=15)], ["Boundary"]
        )
        self.assertEqual(self.rank(["egg"], max_time=1), [])
        self.assertIsNone(match_recipes(["egg"], max_time=1, data_path=self.data_path))

    def test_use_soon_changes_winner_and_preserves_missing_items(self):
        self.write_recipes([
            ("Egg rice", "10 mins", ["egg", "rice"]),
            ("Spinach rice", "10 mins", ["spinach", "rice"]),
        ])
        pantry = ["egg", "spinach"]
        self.assertEqual(self.rank(pantry)[0]["title"], "Egg rice")
        winner = self.rank(pantry, use_soon=["spinach"])[0]
        self.assertEqual(winner["title"], "Spinach rice")
        self.assertAlmostEqual(winner["score"], 1.5 / 2.5)
        self.assertEqual(winner["matched_ingredients"], ["spinach"])
        self.assertEqual(winner["missing_ingredients"], ["rice"])

    def test_limit_and_small_dataset(self):
        self.write_recipes([("Egg", "5 mins", ["egg"])])
        self.assertEqual(len(self.rank(["egg"])), 1)
        self.assertEqual(len(self.rank(["egg"], limit=1)), 1)
        for limit in (0, -1, True, 1.5, "3"):
            with self.subTest(limit=limit), self.assertRaises(ValueError):
                self.rank(["egg"], limit=limit)

    def test_staples_only_and_empty_pantries_rejected(self):
        for pantry in ([], ["salt", "water"], ["olive oil", "black pepper"]):
            with self.subTest(pantry=pantry), self.assertRaises(ValueError):
                self.rank(pantry)

    def test_repository_dataset(self):
        result = rank_recipes(["chicken", "egg", "rice"], max_time=30)
        self.assertEqual(len(result), 3)
        self.assertTrue(all(r["time_minutes"] <= 30 for r in result))
        self.assertEqual([r["score"] for r in result],
                         sorted([r["score"] for r in result], reverse=True))


if __name__ == "__main__":
    unittest.main()
