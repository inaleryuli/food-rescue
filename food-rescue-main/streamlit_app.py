"""Browser interface for the existing Food Rescue recipe engine."""

import re
from html import escape

import streamlit as st

from src.service import search_food_rescue
from src.agent import explain_recipe, chat_about_recipe, MAX_QUESTION_LENGTH
from src.validation import check_safety, InputError, MAX_PANTRY_INGREDIENTS
from src.normalizer import normalize_ingredient


PRESETS = (
    ("Chicken & broccoli", ["chicken breast", "broccoli", "garlic", "soy sauce"], ["broccoli"], 40),
    ("Mushroom dinner", ["chicken breast", "mushroom", "butter"], ["mushroom"], 30),
    ("Honey chicken", ["chicken breast", "honey", "garlic"], [], 25),
)
MAX_INGREDIENTS = MAX_PANTRY_INGREDIENTS


def ai_settings() -> dict:
    try:
        return {name: str(st.secrets[name]) for name in
                ("BAILIAN_API_KEY", "BAILIAN_BASE_URL", "BAILIAN_MODEL") if name in st.secrets}
    except FileNotFoundError:
        return {}


def clear_recipe_chat(title: str) -> None:
    st.session_state.recipe_chats[title] = []


def render_recipe_chat(recipe: dict, use_soon: list[str], index: int, live_ai: bool) -> None:
    st.markdown("#### Your cooking assistant")
    if not live_ai:
        st.info(explain_recipe(recipe, use_soon)["text"])
        st.caption("Offline overview. Enable 'Use live AI' above to ask questions about this recipe.")
        return
    st.caption("Ask about this recipe's steps or ingredients. AI can make mistakes; check the original instructions.")
    turns = st.session_state.recipe_chats.setdefault(recipe["title"], [])
    if turns:
        st.button("Clear conversation", key=f"clear_chat_{index}", on_click=clear_recipe_chat, args=(recipe["title"],))
    for turn in turns:
        with st.chat_message("user"):
            st.write(turn["question"])
        with st.chat_message("assistant"):
            st.write(turn["text"])
            st.caption(turn["status"])
    steps, shopping = st.columns(2)
    question = None
    if steps.button("Explain the steps", key=f"chat_steps_{index}", use_container_width=True):
        question = "Walk me through this recipe in simple steps. Keep the original quantities, times and temperatures."
    if shopping.button("What do I need to buy?", key=f"chat_shopping_{index}", use_container_width=True):
        question = "What am I missing for this recipe? Use the source quantities where available."
    typed = st.chat_input("Ask about these steps or ingredients…", key=f"chat_input_{index}", max_chars=MAX_QUESTION_LENGTH)
    if typed or question:
        question = typed or question
        history = [message for turn in turns if turn["mode"] == "live_ai" for message in
                   ({"role": "user", "content": turn["question"]}, {"role": "assistant", "content": turn["text"]})]
        with st.spinner("Thinking about your recipe..."):
            reply = chat_about_recipe(recipe, question, history, use_soon, settings=ai_settings())
        st.session_state.recipe_chats[recipe["title"]] = (turns + [{"question": question, **reply}])[-10:]
        st.rerun()


def contains_non_food(item: str) -> bool:
    """Catch known non-food examples before calling the recipe engine."""
    try:
        check_safety([item])
    except InputError:
        return True
    return False


def add_ingredient() -> None:
    raw = st.session_state.ingredient_draft.strip()
    st.session_state.ingredient_draft = ""
    if not raw:
        return
    st.session_state.search_submitted = False
    if contains_non_food(raw):
        try:
            check_safety([raw])
        except InputError as error:
            st.session_state.input_error = str(error)
        return
    ingredient = normalize_ingredient(raw)
    if not ingredient:
        st.session_state.input_error = "Enter an ingredient name, such as broccoli."
    elif ingredient in st.session_state.pantry:
        st.session_state.input_error = f"{ingredient.title()} is already on your list."
    elif len(st.session_state.pantry) >= MAX_INGREDIENTS:
        st.session_state.input_error = "You can add up to 25 ingredients."
    else:
        st.session_state.pantry.append(ingredient)
        st.session_state[f"soon_{ingredient}"] = False
        st.session_state.input_error = ""


def remove_ingredient(ingredient: str) -> None:
    if ingredient not in st.session_state.pantry:
        return
    st.session_state.pantry.remove(ingredient)
    st.session_state.use_soon.discard(ingredient)
    st.session_state.pop(f"soon_{ingredient}", None)
    st.session_state.search_submitted = False


def set_use_soon(ingredient: str) -> None:
    # Browser events can arrive after a preset/clear removed the old widget.
    if ingredient not in st.session_state.pantry:
        return
    if st.session_state.get(f"soon_{ingredient}", False):
        st.session_state.use_soon.add(ingredient)
    else:
        st.session_state.use_soon.discard(ingredient)
    st.session_state.search_submitted = False


def load_preset(pantry: list[str], use_soon: list[str], minutes: int) -> None:
    for old in st.session_state.pantry:
        st.session_state.pop(f"soon_{old}", None)
    st.session_state.pantry = pantry.copy()
    st.session_state.use_soon = set(use_soon)
    st.session_state.max_time = minutes
    st.session_state.input_error = ""
    st.session_state.ingredient_draft = ""
    st.session_state.search_submitted = True
    for ingredient in pantry:
        st.session_state[f"soon_{ingredient}"] = ingredient in use_soon


def clear_pantry() -> None:
    for ingredient in st.session_state.pantry:
        st.session_state.pop(f"soon_{ingredient}", None)
    st.session_state.pantry = []
    st.session_state.ingredient_draft = ""
    st.session_state.use_soon = set()
    st.session_state.input_error = ""
    st.session_state.search_submitted = False


st.set_page_config(page_title="Food Rescue", page_icon="🍳", layout="wide")

if "pantry" not in st.session_state:
    st.session_state.pantry = []
if "use_soon" not in st.session_state:
    st.session_state.use_soon = set()
if "input_error" not in st.session_state:
    st.session_state.input_error = ""
if "search_submitted" not in st.session_state:
    st.session_state.search_submitted = False
if "max_time" not in st.session_state:
    st.session_state.max_time = 40

st.markdown(
    """<style>
    .block-container {max-width: 1280px; padding-top: 4.5rem; padding-bottom: 2rem;}
    h1, h2, h3 {letter-spacing: -.035em;}
    h3 {font-size: 1.35rem !important;}
    .brand {font-size: .8rem; font-weight: 750; letter-spacing: .15em;
            text-transform: uppercase; color: #285c43; margin-bottom: 1.5rem;}
    .hero {background: #e9efe4; border: 1px solid #d8e3d3; border-radius: 24px;
           padding: 2rem 2.4rem; margin-bottom: 1.8rem; position: relative; overflow: hidden;}
    .hero h1 {font-size: clamp(2rem, 4vw, 3.3rem); line-height: 1.08;
              max-width: 700px; padding: 0 0 .8rem; color: #1d4432;}
    .hero p {color: #4c6353; margin: 0; max-width: 590px;}
    .eyebrow {font-size: .72rem; font-weight: 700; letter-spacing: .13em;
              text-transform: uppercase; color: #66694d; margin-bottom: .7rem;}
    .st-key-pantry_panel {background: #fff; border-radius: 20px; padding: 1.25rem;
                          border-color: #e0e4d9;}
    [class*="st-key-recipe_card_"] {background: #fff; border-radius: 20px;
                                    border-color: #e0e4d9; padding: 1.4rem;}
    .recipe-meta {display: flex; gap: .5rem; flex-wrap: wrap; margin: .25rem 0 1rem;}
    .recipe-meta span {background: #f2f3ed; color: #4c594e; padding: .3rem .65rem;
                       border-radius: 7px; font-size: .8rem; font-weight: 600;}
    .recipe-meta .coverage {background: #e8f1e5; color: #2c603d;}
    .recipe-meta .missing {background: #fbf0df; color: #80551f;}
    .ingredients {font-size: .95rem; line-height: 1.65; margin-bottom: .8rem;}
    .ingredients b {font-size: .7rem; letter-spacing: .09em; text-transform: uppercase;
                    display: block; color: #526b58; margin-bottom: .15rem;}
    .ingredients.need b {color: #80551f;}
    .empty-state {border: 1px dashed #cdd9c8; border-radius: 20px; text-align: center;
                  padding: 3rem 1.5rem; margin-top: 1rem; background: #f1f4ec;}
    .empty-state h3 {color: #36553e;}
    .empty-state p {color: #61715e; max-width: 360px; margin: auto;}
    .stButton button, .stDownloadButton button, .stLinkButton a {border-radius: 10px;}
    .stButton button[kind="primary"] {min-height: 2.9rem;}
    [data-testid="stCaptionContainer"] {opacity: 1;}
    [data-testid="stCaptionContainer"] p {color: #59675b;}
    @media (max-width: 700px) {
      .block-container {padding: 4.5rem 1rem 1rem;}
      .hero {padding: 1.5rem; border-radius: 18px;}
      .st-key-pantry_panel, [class*="st-key-recipe_card_"] {padding: 1rem;}
      .st-key-pantry_panel [data-testid="stHorizontalBlock"] {flex-wrap: nowrap;}
      .st-key-pantry_panel [data-testid="stColumn"]:first-child {flex: 1 1 0; min-width: 0;}
      .st-key-pantry_panel [data-testid="stColumn"]:last-child {flex: 0 0 85px; min-width: 0;}
    }
    </style>""",
    unsafe_allow_html=True,
)

st.markdown('<div class="brand">Food Rescue / The student kitchen</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="hero"><div class="eyebrow">Less guessing. More cooking.</div>'
    '<h1>Good food starts with<br>what you have.</h1>'
    '<p>Find a dinner for your ingredients, your schedule, and the food you want to use soon.</p></div>',
    unsafe_allow_html=True,
)

st.subheader("Try an example")
preset_columns = st.columns(3)
for column, (label, pantry, soon, minutes) in zip(preset_columns, PRESETS):
    column.button(label, use_container_width=True, on_click=load_preset, args=(pantry, soon, minutes))

kitchen, matches = st.columns([1, 1.8], gap="large")
with kitchen, st.container(border=True, key="pantry_panel"):
    st.subheader("Your pantry")
    st.caption("A few ingredients. Plenty of possibilities.")
    entry, add = st.columns([4, 1], vertical_alignment="bottom")
    entry.text_input(
        "Add one ingredient at a time",
        placeholder="Try: broccoli, eggs, or 2 chicken breasts",
        key="ingredient_draft",
        on_change=add_ingredient,
    )
    add.button("Add", use_container_width=True, on_click=add_ingredient)
    if st.session_state.input_error:
        st.error(st.session_state.input_error)

    if st.session_state.pantry:
        st.caption("Tick ingredients you want to use soon. Remove anything you added by mistake.")
        for ingredient in st.session_state.pantry:
            check, remove = st.columns([3, 1.4])
            check.checkbox(
                ingredient.title(),
                key=f"soon_{ingredient}",
                on_change=set_use_soon,
                args=(ingredient,),
            )
            remove.button("Remove", key=f"remove_{ingredient}", on_click=remove_ingredient, args=(ingredient,))
        st.button("Clear all", on_click=clear_pantry)
    else:
        st.caption("Add at least one main ingredient, or choose an example above.")

    st.slider(
        "Maximum cooking time (minutes)",
        min_value=10,
        max_value=120,
        step=5,
        key="max_time",
        on_change=lambda: st.session_state.update(search_submitted=False),
    )
    st.button("Find recipes", type="primary", use_container_width=True, on_click=lambda: st.session_state.update(search_submitted=True))

with matches:
    st.subheader("On the menu")
    live_ai = st.checkbox("Use live AI (optional)", value=False, key="live_ai")
    if live_ai:
        st.caption("Chat uses the selected recipe, matched/missing ingredients and recent messages. Keep personal details out of the chat.")
    signature = (tuple(st.session_state.pantry), tuple(sorted(st.session_state.use_soon)),
                 st.session_state.max_time, live_ai)
    if st.session_state.get("recipe_context") != signature:
        st.session_state.recipe_context = signature
        st.session_state.recipe_chats = {}
        st.session_state.active_recipe = None

    if st.session_state.search_submitted:
        if not st.session_state.pantry:
            st.warning("Add at least one main ingredient to search.")
        else:
            try:
                payload = search_food_rescue(
                    st.session_state.pantry,
                    use_soon=st.session_state.use_soon,
                    max_time=st.session_state.max_time,
                    limit=3,
                )
            except ValueError as error:
                st.warning(str(error))
            else:
                results = payload["recipes"]
                if payload["status"] != "ok":
                    st.warning(payload["message"])
                else:
                    st.caption("Match score is the share of each recipe's weighted ingredients you have, not a food-safety rating.")
                    with st.expander("How these matches were selected"):
                        st.write("We normalize ingredient names, exclude recipes over your time limit, and rank the remaining recipes by weighted pantry coverage. Use-soon items weigh 1.5, staples 0.5, other ingredients 1.0. A higher score does not guarantee every main ingredient is available or that every use-soon item is used.")
                        st.write("Recognized pantry:", ", ".join(payload["query"]["pantry"]))
                    for index, recipe in enumerate(results):
                        with st.container(border=True, key=f"recipe_card_{index}"):
                            st.caption("TOP MATCH" if index == 0 else f"ANOTHER IDEA · {index + 1:02d}")
                            st.subheader(recipe["title"])
                            st.markdown(
                                f'<div class="recipe-meta"><span class="coverage">{recipe["score"]:.0%} match</span>'
                                f'<span>{recipe["time_minutes"]} min</span>'
                                f'<span class="missing">{len(recipe["missing_ingredients"])} missing</span></div>',
                                unsafe_allow_html=True,
                            )
                            have, need = st.columns(2)
                            have.markdown('<div class="ingredients"><b>In your kitchen</b>' +
                                          escape(", ".join(recipe["matched_ingredients"]) or "None") + '</div>', unsafe_allow_html=True)
                            need.markdown('<div class="ingredients need"><b>Pick up</b>' +
                                          escape(", ".join(recipe["missing_ingredients"]) or "Nothing else") + '</div>', unsafe_allow_html=True)
                            shopping, help_button = st.columns(2)
                            shopping.download_button(
                                "Export shopping list",
                                data=recipe["title"] + "\n\n" + ("\n".join("- " + item for item in recipe["missing_ingredients"]) or "Nothing else needed.") + "\n\nCheck quantities in the source recipe before shopping.\n",
                                file_name="shopping-list-" + re.sub(r"[^a-z0-9]+", "-", recipe["title"].lower()).strip("-") + ".txt",
                                mime="text/plain", key="shop_" + recipe["title"], use_container_width=True,
                                on_click="ignore",
                            )
                            if help_button.button("Help me cook this", key=f"explain_{index}", use_container_width=True):
                                st.session_state.active_recipe = recipe["title"]
                                st.rerun()
                            if st.session_state.active_recipe == recipe["title"]:
                                render_recipe_chat(recipe, payload["query"]["use_soon"], index, live_ai)
                            with st.expander("Cooking instructions"):
                                if recipe.get("servings"):
                                    st.write("Source servings:", recipe["servings"])
                                st.write("**Recipe ingredients and available measures:**")
                                for detail in recipe["ingredient_details"]:
                                    st.write("• " + detail)
                                st.caption("Some imported rows omit measurements. Open the original recipe for complete quantities; pantry amounts are not checked.")
                                if recipe.get("source_url", "").startswith("https://"):
                                    st.link_button("Open original recipe", recipe["source_url"])
                                steps = recipe["instructions"].splitlines()
                                if steps:
                                    for number, step in enumerate(steps, start=1):
                                        st.write(f"{number}. {step}")
                                else:
                                    st.write("Instructions are unavailable for this recipe.")
                                st.caption("Check ingredient packaging for allergen and cross-contamination information.")
    else:
        st.markdown(
            '<div class="empty-state"><div class="eyebrow">Your next meal awaits</div>'
            '<h3>Start with what’s in the fridge.</h3>'
            '<p>Add your ingredients or try an example above. Your recipe matches will appear here.</p></div>',
            unsafe_allow_html=True,
        )


st.caption("Check ingredient freshness and packaging yourself. Food Rescue cannot assess food safety or allergens.")
st.divider()
with st.expander("About Food Rescue · project, evidence and limitations"):
    st.write("Built for students deciding what to cook from an English pantry list. The team built the normalizer, weighted matching rules, shared refusal checks, shopping-list export, browser app, CLI and MCP tool. Streamlit supplies the interface framework; optional Qwen answers follow-up questions using the selected recipe.")
    st.link_button("Source code and setup", "https://github.com/rodri-hu-cl/food-rescue")
    st.write("The fixed dataset contains 1,018 recipe titles. Suggestions may require shopping. Times come from source data and are not guarantees; unknown times are excluded when a time limit is set. Keyword guards cannot certify that an ingredient is edible. No nutrition, allergen, dietary or freshness guarantees; no measured food-waste reduction.")
    st.write("Pantry and chat history stay in the current session; changing your search clears the chats. AI receives the selected recipe and recent messages. Keep personal or sensitive information out of entries.")
