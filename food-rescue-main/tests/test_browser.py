"""Exercise real Streamlit callbacks and rendered results without a model key."""
import importlib.util
import unittest
from pathlib import Path
from unittest.mock import patch

from src.service import search_food_rescue


@unittest.skipUnless(importlib.util.find_spec("streamlit"), "Install requirements.txt for browser tests")
class BrowserTests(unittest.TestCase):
    def app(self):
        from streamlit.testing.v1 import AppTest
        return AppTest.from_file(str(Path(__file__).resolve().parents[1] / "streamlit_app.py")).run(timeout=15)

    def test_presets_render_cards_shopping_lists_and_explanation(self):
        for index in range(3):
            with self.subTest(preset=index):
                app = self.app()
                app.button[index].click().run()
                self.assertFalse(app.exception)
                self.assertFalse(app.warning)
                self.assertEqual(len(app.get("download_button")), 3)
                next(b for b in app.button if b.label == "Help me cook this").click().run()
                self.assertFalse(app.exception)
                self.assertTrue(any("Offline overview" in c.value for c in app.caption))
                next(b for b in app.button if b.label == "Clear all").click().run()
                self.assertFalse(app.exception)
                self.assertEqual(app.session_state["pantry"], [])

    def test_add_normalize_use_soon_remove_clear_and_staples_refusal(self):
        app = self.app()
        app.text_input(key="ingredient_draft").set_value("2 large eggs").run()
        self.assertEqual(app.session_state["pantry"], ["egg"])
        app.checkbox(key="soon_egg").check().run()
        self.assertEqual(app.session_state["use_soon"], {"egg"})
        next(b for b in app.button if b.label == "Find recipes").click().run()
        self.assertEqual(len(app.get("download_button")), 3)
        next(b for b in app.button if b.key == "remove_egg").click().run()
        self.assertEqual(app.session_state["pantry"], [])
        self.assertFalse(app.session_state["search_submitted"])
        app.text_input(key="ingredient_draft").set_value("salt").run()
        next(b for b in app.button if b.label == "Find recipes").click().run()
        self.assertTrue(any("core ingredient" in w.value for w in app.warning))
        next(b for b in app.button if b.label == "Clear all").click().run()
        self.assertEqual(app.session_state["pantry"], [])
        self.assertFalse(app.exception)

    def test_bad_inputs_are_visible_and_never_added(self):
        app = self.app()
        for item in ("bleach", "mouldy chicken", "½"):
            app.text_input(key="ingredient_draft").set_value(item).run()
            self.assertTrue(app.error)
            self.assertEqual(app.session_state["pantry"], [])
        self.assertFalse(app.exception)

    def test_selected_recipe_chat_remembers_followups_and_clears_with_search(self):
        app = self.app()
        app.button[0].click().run()
        app.checkbox(key="live_ai").check().run()
        expected = search_food_rescue(["chicken breast", "broccoli", "garlic", "soy sauce"], ["broccoli"], 40)["recipes"][1]
        reply = {"mode": "live_ai", "status": "AI response", "text": "Follow the original steps."}
        with patch("src.agent.chat_about_recipe", return_value=reply) as chat:
            app.button(key="explain_1").click().run()
            chat.assert_not_called()
            app.chat_input(key="chat_input_1").set_value("Explain the first step.").run()
            self.assertFalse(app.exception)
            self.assertEqual(chat.call_args.args[0], expected)
            self.assertEqual(chat.call_args.args[2], [])
            app.run()
            self.assertEqual(chat.call_count, 1)
            app.chat_input(key="chat_input_1").set_value("What comes after that?").run()
            self.assertEqual(chat.call_count, 2)
            self.assertEqual(chat.call_args.args[2], [
                {"role": "user", "content": "Explain the first step."},
                {"role": "assistant", "content": reply["text"]},
            ])
            app.button(key="explain_0").click().run()
            app.chat_input(key="chat_input_0").set_value("What do I need?").run()
            self.assertEqual(chat.call_args.args[2], [])
            app.button(key="explain_1").click().run()
            self.assertEqual(len(app.session_state["recipe_chats"][expected["title"]]), 2)
            app.button(key="clear_chat_1").click().run()
            self.assertEqual(app.session_state["recipe_chats"][expected["title"]], [])
            self.assertEqual(chat.call_count, 3)
            app.slider(key="max_time").set_value(45).run()
            self.assertEqual(app.session_state["recipe_chats"], {})
            self.assertIsNone(app.session_state["active_recipe"])

    def test_cloud_secrets_and_visible_fallback_without_automatic_retry(self):
        app = self.app()
        app.secrets.update({"BAILIAN_API_KEY": "cloud-test-key", "BAILIAN_BASE_URL": "https://example.invalid/v1", "BAILIAN_MODEL": "test-model"})
        app.button[0].click().run()
        app.checkbox(key="live_ai").check().run()
        reply = {"mode": "offline_fallback", "status": "AI is unavailable", "text": "Please try again."}
        with patch("src.agent.chat_about_recipe", return_value=reply) as chat:
            app.button(key="explain_2").click().run()
            app.button(key="chat_steps_2").click().run()
            self.assertFalse(app.exception)
            self.assertEqual(chat.call_args.kwargs["settings"]["BAILIAN_API_KEY"], "cloud-test-key")
            self.assertTrue(any(c.value == reply["status"] for c in app.caption))
            app.run()
            chat.assert_called_once()
            app.chat_input(key="chat_input_2").set_value("Try the first step again.").run()
            self.assertEqual(chat.call_args.args[2], [])
            app.checkbox(key="live_ai").uncheck().run()
            self.assertEqual(app.session_state["recipe_chats"], {})
            self.assertFalse(any("cloud-test-key" in str(c.value) for c in app.markdown))


if __name__ == "__main__":
    unittest.main()
