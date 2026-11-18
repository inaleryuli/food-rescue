"""Regressions for the final shared contract, dataset importer and AI failures."""
import csv
import importlib.util
import json
import os
import subprocess
import sys
import tempfile
import types
import unittest
from pathlib import Path
from unittest.mock import patch

from src.agent import explain_recipe, run_food_rescue, chat_about_recipe
from src.engine import _direction_text, _matches, load_recipes, rank_recipes
from src.mcp_server import handle_message
from src.service import search_food_rescue
from scripts.import_recipe_dataset import _ingredient_records, import_dataset


class ContractTests(unittest.TestCase):
    def test_all_entry_points_refuse_overload_before_normalization(self):
        pantry = ["egg"] * 26
        with self.assertRaisesRegex(ValueError, "Overload"):
            rank_recipes(pantry)
        self.assertIn("Overload", run_food_rescue(pantry))
        payload = handle_message({"jsonrpc": "2.0", "id": 1, "method": "tools/call",
                                  "params": {"name": "search_food_rescue", "arguments": {"pantry": pantry}}})
        self.assertEqual(payload["result"]["structuredContent"]["reason"], "overload")

    def test_hazard_priority_and_both_lists(self):
        with patch("src.engine.load_recipes", side_effect=AssertionError("must not load")):
            result = search_food_rescue(["salt"] * 26, ["bleach"])
            self.assertEqual(result["reason"], "non_food")
            self.assertEqual(search_food_rescue(["rice", "motor-oil"])["reason"], "non_food")
            self.assertEqual(search_food_rescue(["rice", "ＢＬＥＡＣＨ"])["reason"], "non_food")

    def test_scope_refusals(self):
        for item in ("mouldy chicken", "expired eggs", "is this still safe", "allergen-free rice", "diabetes diet"):
            with self.subTest(item=item):
                self.assertEqual(search_food_rescue([item])["reason"], "out_of_scope")

    def test_input_contract_and_real_no_matches(self):
        for minutes in (0, -2, True, 1.5, "15"):
            with self.subTest(minutes=minutes):
                self.assertEqual(search_food_rescue(["rice"], max_time=minutes)["status"], "refused")
        self.assertEqual(search_food_rescue([None])["status"], "refused")
        self.assertEqual(search_food_rescue(["egg"], ["spinach"])["status"], "refused")
        self.assertEqual(search_food_rescue(["unobtainium", "salt"])["status"], "no_matches")
        self.assertEqual(search_food_rescue(["egg"], max_time=1)["status"], "no_matches")

    def test_aliases_and_derived_products(self):
        self.assertTrue(_matches("scallion", "chopped green onions"))
        self.assertTrue(_matches("courgette", "zucchini"))
        self.assertFalse(_matches("chicken", "chicken broth"))
        self.assertFalse(_matches("chicken", "chicken broth, low sodium"))
        self.assertFalse(_matches("garlic", "garlic powder"))

    def test_dataset_unavailable_is_a_clear_error(self):
        with patch("src.engine.load_recipes", side_effect=FileNotFoundError):
            result = search_food_rescue(["egg"])
        self.assertEqual(result["reason"], "dataset_unavailable")
        self.assertEqual(result["recipes"], [])

    def test_source_quantities_short_steps_and_cache_isolation(self):
        self.assertEqual(_direction_text(repr(["Mix well", "Serve", "Photo by someone"])), "Mix well\nServe")
        recipes = load_recipes()
        self.assertEqual(len(recipes), 1018)
        self.assertTrue(all(r["source_url"].startswith("https://www.allrecipes.com/") for r in recipes))
        recipes[0]["ingredients"].clear()
        self.assertTrue(load_recipes()[0]["ingredients"])
        self.assertTrue(all(r["ingredient_details"] for r in rank_recipes(["egg", "rice"])))

    def test_cache_invalidates_after_dataset_change(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "recipes.csv"
            path.write_text('Name,Ingredients,Directions\nFirst,"[\'egg\']","[\'Serve.\']"\n', encoding="utf-8")
            self.assertEqual(load_recipes(path)[0]["title"], "First")
            path.write_text('Name,Ingredients,Directions\nSecond,"[\'rice\']","[\'Serve.\']"\n', encoding="utf-8")
            self.assertEqual(load_recipes(path)[0]["title"], "Second")

    def test_importer_preserves_food_prefixes_fractions_and_quantities(self):
        records = _ingredient_records("1 cantaloupe, ½ cup sugar, 1½ cups milk, 2 lemons, 2 (14 ounce) cans tomatoes")
        self.assertEqual([r["name"] for r in records], ["cantaloupe", "sugar", "milk", "lemons", "tomatoes"])
        self.assertEqual(records[1]["quantity"], "½")
        self.assertEqual(records[2]["quantity"], "1½")
        self.assertEqual(records[4]["unit"], "(14 ounce) cans")

    def test_importer_is_idempotent(self):
        with tempfile.TemporaryDirectory() as directory:
            source, output = Path(directory) / "source.csv", Path(directory) / "output.csv"
            with source.open("w", newline="", encoding="utf-8") as f:
                writer = csv.DictWriter(f, fieldnames=["recipe_name", "ingredients", "directions"])
                writer.writeheader()
                writer.writerow({"recipe_name": "Test", "ingredients": "2 eggs", "directions": "Cook eggs."})
            self.assertEqual(import_dataset(source, output), 1)
            content = output.read_bytes()
            self.assertEqual(import_dataset(source, output), 1)
            self.assertEqual(content, output.read_bytes())

    def test_legacy_imports_are_the_same_implementation(self):
        import engine
        import normalizer
        from src.normalizer import normalize_ingredient
        self.assertIs(engine.rank_recipes, rank_recipes)
        self.assertIs(normalizer.normalize_ingredient, normalize_ingredient)

    @unittest.skipUnless(importlib.util.find_spec("openai"), "Install requirements.txt for optional AI tests")
    def test_recipe_chat_context_settings_and_failed_responses(self):
        recipe = search_food_rescue(["egg", "rice"])["recipes"][0]
        response = types.SimpleNamespace(choices=[types.SimpleNamespace(
            message=types.SimpleNamespace(content="Read the source steps in order."), finish_reason="stop")])
        env = {"BAILIAN_API_KEY": "test-key", "BAILIAN_MODEL": "test-model", "BAILIAN_BASE_URL": "https://example.invalid/v1"}
        with patch.dict(os.environ, env), patch("openai.OpenAI") as client:
            api = client.return_value.__enter__.return_value
            api.chat.completions.create.return_value = response
            before = json.dumps(recipe)
            history = [{"role": "system", "content": "UNTRUSTED ROLE"},
                       {"role": "user", "content": "What is the first step?"},
                       {"role": "assistant", "content": "Start with the source instructions."}]
            result = chat_about_recipe(recipe, "And then?", history, settings={"BAILIAN_API_KEY": "cloud-key"})
            self.assertEqual(result["mode"], "live_ai")
            client.assert_called_once_with(api_key="cloud-key", base_url="https://example.invalid/v1", timeout=30.0, max_retries=0)
            messages = api.chat.completions.create.call_args.kwargs["messages"]
            self.assertEqual(messages[-1], {"role": "user", "content": "And then?"})
            self.assertIn(recipe["instructions"], json.loads(messages[1]["content"].split("\n", 1)[1])["instructions"])
            self.assertEqual(messages[-3:-1], history[-2:])
            self.assertNotIn("UNTRUSTED ROLE", json.dumps(messages))
            self.assertNotIn("cloud-key", json.dumps(messages))
            self.assertIn("Never invent missing measurements", messages[0]["content"])
            self.assertEqual(os.environ["BAILIAN_API_KEY"], "test-key")
            self.assertEqual(explain_recipe(recipe, use_ai=True)["mode"], "live_ai")
            for content, finish in (("", "stop"), (None, "stop"), ("incomplete", "length")):
                response.choices[0].message.content = content
                response.choices[0].finish_reason = finish
                self.assertEqual(chat_about_recipe(recipe, "Explain this.")["mode"], "offline_fallback")
            api.chat.completions.create.side_effect = TimeoutError("secret text")
            fallback = chat_about_recipe(recipe, "Explain this.")
            self.assertEqual(fallback["mode"], "offline_fallback")
            self.assertNotIn("secret text", str(fallback))
            self.assertEqual(json.dumps(recipe), before)

    @unittest.skipUnless(importlib.util.find_spec("openai"), "Install requirements.txt for optional AI tests")
    def test_chat_limits_refusals_and_missing_key_make_no_request(self):
        recipe = search_food_rescue(["egg", "rice"])["recipes"][0]
        with patch("openai.OpenAI") as client:
            for question in ("", "x" * 1001, "Can I use bleach?", "Is expired chicken safe to eat?", "Is this allergen free?"):
                self.assertEqual(chat_about_recipe(recipe, question)["mode"], "refused")
            self.assertEqual(chat_about_recipe(recipe, "What do I buy?", settings={"BAILIAN_API_KEY": ""})["mode"], "offline_fallback")
            client.assert_not_called()

    def test_mcp_real_stdio_and_parse_error_recovery_from_other_cwd(self):
        root = Path(__file__).resolve().parents[1]
        messages = ["broken json", json.dumps({"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {"protocolVersion": "2099-01-01"}}),
                    json.dumps({"jsonrpc": "2.0", "method": "notifications/initialized"}),
                    json.dumps({"jsonrpc": "2.0", "id": 2, "method": "tools/call", "params": {"name": "search_food_rescue", "arguments": {"pantry": ["rice", "bleach"]}}}),
                    json.dumps({"jsonrpc": "2.0", "id": 3, "method": "tools/call", "params": {"name": "search_food_rescue", "arguments": {"pantry": ["egg", "rice"], "max_time": 15}}})]
        with tempfile.TemporaryDirectory() as directory:
            result = subprocess.run([sys.executable, str(root / "src/mcp_server.py")], input="\n".join(messages) + "\n",
                                    capture_output=True, text=True, encoding="utf-8", cwd=directory, timeout=15)
        self.assertEqual(result.returncode, 0, result.stderr)
        replies = [json.loads(line) for line in result.stdout.splitlines()]
        self.assertEqual(len(replies), 4)
        self.assertEqual(replies[0]["error"]["code"], -32700)
        self.assertEqual(replies[1]["result"]["protocolVersion"], "2025-06-18")
        self.assertEqual(replies[2]["result"]["structuredContent"]["reason"], "non_food")
        self.assertEqual(replies[3]["result"]["structuredContent"]["status"], "ok")


if __name__ == "__main__":
    unittest.main()
