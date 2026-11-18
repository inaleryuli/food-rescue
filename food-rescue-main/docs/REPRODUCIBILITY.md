# Reproduce Food Rescue

The recorded environment is Python 3.14.7 on Windows. The runtime works offline once dependencies are installed. CLI/MCP require only Python's standard library. Exact dependency versions are in `requirements-lock.txt`; direct runtime versions are in `requirements.txt`.

## Fresh checkout

```powershell
git clone https://github.com/rodri-hu-cl/food-rescue.git
cd food-rescue
python -m venv .venv
.\.venv\Scripts\python -m pip install -r requirements-lock.txt
.\.venv\Scripts\python -m unittest discover -s tests -v
.\.venv\Scripts\python src/mcp_server.py --test
.\.venv\Scripts\python benchmark.py --repeats 3
.\.venv\Scripts\python scripts/evaluate.py
.\.venv\Scripts\python run_local.py
```

This final revision must be committed/pushed before a remote clone contains it. The local review includes a clean source-copy check in `evidence/reproduction.txt`; it is not a claim that unpublished changes already exist on GitHub. For Unix, substitute `.venv/bin/python`.

## Expected behaviour

- Three presets run without a key. Each result lists matches, missing ingredients, available source measures, source link, instructions and a shopping-list download.
- `python -m src.app --pantry "chicken breast" mushroom butter flour --use-soon mushroom --max-time 30 --json` leads with Chicken Marsala, 50%, 30 minutes.
- `python -m src.app --pantry chicken bleach --json` returns `refused`, reason `non_food`, with zero recipes.
- `python -m src.app --pantry salt water --json` asks for a core ingredient.
- `python -m src.app --pantry unobtainium --json` returns `no_matches`.
- The ten proposal scenarios and integration/browser tests pass; two intentionally unsupported normalization cases are reported as failures in quality evaluation, independently of regression test correctness.

## Evidence scope

`evidence/evaluation.json` records dataset and source-code hashes, UTC generation time, platform, case-level outputs and cold/warm service timing. `evidence/benchmark.txt` records repeated proposal scenarios. Its use-soon scenarios use isolated fixtures, while standard pantry/time scenarios use the real CSV. `evidence/browser-smoke.json` and screenshots come from actual local browser execution. AI tests simulate provider outputs/failures; no live model quality or end-to-end 3.5-second claim is established. MCP subprocess testing does not certify an external agent client.

The public page and report use generated evaluation values. After changing the engine/data, rerun `scripts/evaluate.py`, tests and `scripts/build_project_page.py`; rebuild the report review copy. Final remote reproduction, hosting permissions, video links and the exported PDF page count require the group to check the submitted version.

## Secrets

`.env` and `.streamlit/secrets.toml` are excluded. No configuration is required for search or deterministic explanations. If live AI is enabled, use a provider-authorized model/base URL and server-side secret storage. The UI explicitly opts in before sending title/matched-ingredient data. Avoid private information in pantry entries.

## Public hosting

For the project webpage, push this revision and enable GitHub Pages: repository Settings > Pages > Deploy from a branch > `main`, `/docs`. Verify the actual URL returned by GitHub in a signed-out browser before putting it in `submission/links.json`. See [GitHub Pages instructions](https://docs.github.com/en/pages/quickstart).

For a live browser app, use the existing GitHub repository in Streamlit Community Cloud, choose `streamlit_app.py`, and select Python 3.14 if offered. Use the tested dependency pins. If the provider offers a different Python version, install/test that version before changing the pins. No secrets are needed for the offline product. The public project page and live app are separate artifacts; a local-only URL does not satisfy the public webpage requirement. See [Streamlit deployment instructions](https://docs.streamlit.io/deploy/streamlit-community-cloud/deploy-your-app).
