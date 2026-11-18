# Food Rescue

Find existing recipes using ingredients already in your kitchen. The Streamlit app supports pantry editing, use-soon priorities, a cooking-time limit, source recipe instructions and shopping-list downloads. Search works without an account or API key.

## Run the app

Use Python 3.14. From the repository folder:

```powershell
python -m venv .venv
.\.venv\Scripts\python -m pip install -r requirements.txt
.\.venv\Scripts\python run_local.py
```

Open the local URL printed by Streamlit, usually http://localhost:8501. On macOS/Linux, use `.venv/bin/python` instead of `.\.venv\Scripts\python`. Stop the app with Ctrl+C. To change ports, append `--server.port=8502` to the launch command. `requirements-lock.txt` records pinned runtime dependencies.

## Use it

1. Choose a preset or enter ingredients one at a time.
2. Tick the checkbox beside an ingredient to mark it as use-soon.
3. Set the maximum cooking time and click **Find recipes**.
4. Review matched and missing ingredients. Expand **Cooking instructions** for source quantities, servings and the original recipe link.
5. Click **Export shopping list** to download missing ingredients.

Use-soon increases an ingredient's scoring weight; it does not require every result to contain it. For the Chicken & broccoli preset, a 25-minute limit excludes the matching broccoli recipes. At 40 minutes, marking broccoli use-soon brings Broccoli and Chicken Stir-Fry into the top three.

## Matching and limits

The app normalizes English ingredient names and aliases, filters out recipes above the time limit, and ranks by matched ingredient weight divided by total recipe weight. Use-soon ingredients weigh 1.5, staples 0.5, and other ingredients 1.0. Ties use matched ingredient count, then title. Unknown recipe times are excluded when a limit is set. At least one non-staple ingredient must match.

The fixed dataset contains 1,018 recipe titles. Instructions and available quantities come from source recipes. Check quantities in the original recipe: pantry amounts are not compared with required amounts. Dataset attribution, source checksums and processing details are in [data/provenance.json](data/provenance.json). The importer in `scripts/import_recipe_dataset.py` preserves the seed recipes when rebuilding the dataset; run it with `--help` for its arguments.

Matching can favor short recipes, and some source records lack quantities or times. Arbitrary typos and Chinese input are unsupported. Keyword input guards cannot establish food safety. Check freshness and allergens yourself. The app provides no medical or dietary guarantees, and food-waste reduction has not been measured.

## Optional AI explanations

Recipe search and original cooking instructions work immediately. For live AI, set `BAILIAN_API_KEY`, `BAILIAN_BASE_URL` and `BAILIAN_MODEL` as environment variables or in a local `.env` file. The URL and model must match your provider account and region. These are private deployment settings, not values supplied by app visitors. Keep `.env` and `.streamlit/secrets.toml` out of Git.

Run `python scripts/check_ai.py` to check configuration without exposing credentials. `python scripts/check_ai.py --live` makes a real request; success requires `mode: live_ai`. In the browser, tick **Use live AI (optional)** in the results area, open a recipe, and use the recipe chat to ask about steps or missing ingredients.

Live chat sends the selected recipe, matched and missing ingredients, source steps, use-soon matches, your question and recent conversation messages to the provider. The model is instructed to stay within the recipe and preserve source facts; responses are generated text and should be checked against the original recipe. Unavailable, empty or truncated responses show an availability message. The client uses a 30-second network timeout with no retries; this is not an end-to-end timing guarantee. Pantry and conversation history remain in session memory rather than being written by the app. Keep personal details out of questions. Provider and hosting logs depend on deployment settings.

## Tests and command-line tools

With the runtime environment installed:

```powershell
.\.venv\Scripts\python -m unittest discover -s tests -v
.\.venv\Scripts\python src/mcp_server.py --test
.\.venv\Scripts\python scripts/evaluate.py
```

Evaluation writes local results under `evidence/`, which is excluded from Git. AI tests use mocks; they do not certify live provider availability.

The standard-library CLI also works without Streamlit:

```powershell
python run_local.py --cli
python -m src.app --pantry "chicken breast" broccoli garlic "soy sauce" --use-soon broccoli --max-time 40 --json
```

`src/` contains the shared service, matching engine, validation, normalizer, explanation agent, CLI and stdio MCP server. Root `agent.py`, `engine.py` and `normalizer.py` preserve compatibility imports. `mcp.json` configures the MCP tool from the repository folder. `benchmark.py` measures local search timing.
