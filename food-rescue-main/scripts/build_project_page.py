"""Build the public project page and evaluation notes from real run evidence."""
import json
from html import escape
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REPO = "https://github.com/rodri-hu-cl/food-rescue"


def main():
    evidence = json.loads((ROOT / "evidence/evaluation.json").read_text(encoding="utf-8"))
    links = json.loads((ROOT / "submission/links.json").read_text(encoding="utf-8"))
    s = evidence["summary"]
    recipe = evidence["real_run_example"]["recipes"][0]
    failed = [case for case in evidence["retrieval"] if not case["top10_hit"]]
    video_links = " ".join(f'<a class="button secondary" href="{escape(links[key], quote=True)}">{label}</a>'
                           for key, label in (("presentation_youtube", "Presentation"), ("demo_youtube", "Continuous demo"))
                           if links.get(key, "").startswith("https://"))
    live = f'<a class="button" href="{escape(links["live_app"], quote=True)}">Open the app</a>' if links.get("live_app", "").startswith("https://") else '<a class="button" href="#run">Run Food Rescue</a>'
    rows = "".join(f'<tr><td>{escape(case["title"])}</td><td>{escape(", ".join(case["pantry"]))}</td><td>{case["rank"] or "Outside top 100"}</td><td>{"Hit" if case["top10_hit"] else "Miss"}</td></tr>' for case in evidence["retrieval"])
    html = f'''<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<meta name="description" content="Food Rescue: pantry-based recipe search, use-soon priorities, measured results and reproducible code.">
<title>Food Rescue · Group 40</title><style>
:root{{--ink:#193527;--muted:#4c6457;--green:#276640;--paper:#fbfaf4;--line:#d5ded2}}
*{{box-sizing:border-box}}html{{scroll-behavior:smooth}}body{{margin:0;background:var(--paper);color:var(--ink);font:17px/1.65 system-ui,sans-serif}}
a{{color:var(--green)}}a:focus-visible,summary:focus-visible{{outline:3px solid #ad5c18;outline-offset:4px}}
.skip{{position:absolute;left:-10000px}}.skip:focus{{left:1rem;top:1rem;background:white;z-index:5}}
header,main,footer{{max-width:1120px;margin:auto;padding:1.2rem 2rem}}header{{display:flex;align-items:center;justify-content:space-between;border-bottom:1px solid var(--line);gap:1rem}}nav{{display:flex;gap:1.2rem;flex-wrap:wrap}}nav a{{font-size:.9rem;text-decoration:none}}
.brand{{font-weight:800;letter-spacing:-.04em;font-size:1.3rem}}.hero{{padding:4.5rem 0 3rem;max-width:850px}}.eyebrow{{text-transform:uppercase;font-size:.75rem;letter-spacing:.16em;color:var(--muted);font-weight:700}}
h1{{font-size:clamp(2.5rem,6vw,4.4rem);line-height:1.07;letter-spacing:-.06em;margin:1rem 0 1.5rem}}h2{{font-size:2rem;line-height:1.2;letter-spacing:-.04em;margin-top:0}}h3{{line-height:1.25}}
.lead{{font-size:1.25rem;color:var(--muted);max-width:720px}}.button{{display:inline-block;padding:.75rem 1.15rem;border-radius:.4rem;background:var(--green);color:#fff;text-decoration:none;font-weight:650;margin:.5rem .5rem .5rem 0}}.secondary{{background:transparent;color:var(--green);border:1px solid var(--green)}}
section{{padding:2.5rem 0;border-top:1px solid var(--line);scroll-margin-top:1rem}}.grid{{display:grid;grid-template-columns:repeat(3,1fr);gap:1rem}}.card{{padding:1.5rem;border:1px solid var(--line);border-radius:.65rem;background:white}}.metric{{font-size:2.2rem;font-weight:750;letter-spacing:-.05em;line-height:1.2}}.muted,figcaption{{color:var(--muted);font-size:.9rem}}.flow{{padding:1.3rem;border-left:4px solid var(--green);background:#eef2e8}}
pre{{background:#193527;color:#f4f6ed;padding:1.3rem;border-radius:.5rem;overflow:auto;font-size:.85rem;line-height:1.6}}code{{font-size:.9em}}img{{max-width:100%;border:1px solid var(--line);border-radius:.5rem}}figure{{margin:1.5rem 0}}.screens{{display:grid;grid-template-columns:1.5fr 1fr;gap:1rem;align-items:start}}.screens img{{width:100%;max-height:680px;object-fit:cover;object-position:top}}table{{border-collapse:collapse;width:100%;font-size:.9rem}}th,td{{text-align:left;border-bottom:1px solid var(--line);padding:.65rem;vertical-align:top}}.table-wrap{{overflow:auto}}details{{padding:1rem 0}}summary{{cursor:pointer;font-weight:650}}footer{{font-size:.85rem;border-top:1px solid var(--line);color:var(--muted)}}
@media(max-width:700px){{header{{align-items:flex-start;flex-direction:column}}header,main,footer{{padding:1rem 1.25rem}}.hero{{padding:2.5rem 0}}.grid,.screens{{grid-template-columns:1fr}}nav{{gap:.8rem}}}}
</style></head><body><a class="skip" href="#main">Skip to content</a>
<header><a class="brand" href="#main">Food Rescue</a><nav aria-label="Page navigation"><a href="#workflow">Workflow</a><a href="#evidence">Evidence</a><a href="#limits">Limits</a><a href="#run">Run it</a><a href="{REPO}">GitHub</a></nav></header>
<main id="main"><div class="hero"><div class="eyebrow">AILT9019 · Group 40 · Final project</div>
<h1>What can you cook<br>with what you have?</h1><p class="lead">A pantry list, a little time, and ingredients to use soon. Find existing recipes, see what is missing, and take a shopping list with you.</p>
{live}<a class="button secondary" href="{REPO}">Explore the code</a>{video_links}
<p class="muted">No API key required for the core app. Designed for students cooking in small or shared kitchens.</p></div>
<section id="workflow"><div class="eyebrow">From pantry to recipe</div><h2>A small, inspectable workflow.</h2>
<p class="flow">Pantry + use-soon choices + minutes → shared input guards → normalized names and aliases → hard time filter → weighted coverage ranking → top three recipe cards and shopping list.</p>
<div class="grid"><article class="card"><h3>Start with your kitchen</h3><p>Enter one English ingredient at a time or choose a preset. Mark perishables to use soon and set a cooking-time limit.</p></article><article class="card"><h3>Understand the match</h3><p>See pantry coverage, missing ingredients, source quantities and original instructions. The score measures ingredient overlap.</p></article><article class="card"><h3>Keep facts grounded</h3><p>The optional AI selects a matched ingredient to highlight. It cannot rewrite recipe facts or steps; unavailable AI visibly falls back.</p></article></div>
<h3>What our team built</h3><p>Ingredient normalization and regional aliases; weighted matching (use-soon 1.5, staples 0.5, other ingredients 1.0); shared hazard/scope/input checks; browser workflow and shopping-list export; a CLI and MCP tool; repeatable evaluation. Streamlit supplies interface components, Python supplies the runtime, and the existing recipe corpus supplies source recipes. Optional Qwen is accessed through a compatible client.</p>
<p>We retained the midterm's fixed CSV and shared Python service. PostgreSQL, Redis, spaCy and vector search were deferred; cached parsing and deterministic rules keep this 1,018-title version simple to reproduce.</p></section>
<section id="example"><div class="eyebrow">Actual execution</div><h2>A source-grounded result.</h2><p>Measured input: chicken breast, mushroom, butter and flour; mushroom marked use-soon; maximum 30 minutes.</p>
<article class="card"><h3>{escape(recipe['title'])} · {recipe['score']:.0%} match · {recipe['time_minutes']} min</h3><p><strong>You have:</strong> {escape(', '.join(recipe['matched_ingredients']))}</p><p><strong>You need:</strong> {escape(', '.join(recipe['missing_ingredients']))}</p><p><a href="{escape(recipe['source_url'])}">Original recipe and complete directions</a> · <a href="{REPO}/blob/main/evidence/evaluation.json">Check the recorded JSON</a></p></article>
<div class="screens"><figure><img src="assets/browser-results.png" alt="Actual local browser results showing recipe cards, missing ingredients, source quantities and a shopping-list download"><figcaption>Real browser run: the mushroom preset has fewer pantry items than the measured JSON example above, so its order and scores differ.</figcaption></figure><figure><img src="assets/browser-refusal.png" alt="Actual local browser refusal after entering bleach"><figcaption>Boundary case: bleach is refused before recipe lookup. Screenshots are recorded examples; use the app to run new searches.</figcaption></figure></div></section>
<section id="evidence"><div class="eyebrow">Observable evidence</div><h2>Measured results, including misses.</h2><div class="grid"><div class="card"><div class="metric">{s['top10_hits']}/{s['retrieval_total']}</div><p>Known-item Top-10 hits</p></div><div class="card"><div class="metric">{s['normalization_correct']}/{s['normalization_total']}</div><p>Normalization reference matches</p></div><div class="card"><div class="metric">{s['refusals_passed']}/{s['refusals_total']}</div><p>Refusal cases passed</p></div></div>
<p>All {s['time_queries_passed']}/{s['time_queries_total']} time-filter queries passed, covering {s['timed_recipes_checked']} returned recipes. Across three cold-start searches, the maximum measured service time was {s['cold_max_seconds']:.3f} seconds; warm median was {s['warm_median_seconds']:.3f} seconds on the recorded machine.</p>
<p class="muted">{escape(evidence['method'])} Latency measures in-process validation, CSV loading, scoring and response construction; browser/network and live-model latency are excluded. These results do not establish the proposal's end-to-end API or live-LLM SLA.</p>
<details><summary>Inspect all ten retrieval queries</summary><div class="table-wrap"><table><thead><tr><th>Intended recipe</th><th>Three pantry ingredients</th><th>Observed rank</th><th>Top-10</th></tr></thead><tbody>{rows}</tbody></table></div></details>
<p>Regression tests cover the original ten scenarios, browser callbacks, invalid inputs, unavailable data, importer errors, provider timeout/invalid output, and a real MCP subprocess. Optional live AI is tested with mocks; a live browser run checks search, download, refusal and mobile layout.</p><p><a href="{REPO}/blob/main/evidence/evaluation.json">Case-level evidence</a> · <a href="{REPO}/blob/main/evidence/tests.txt">Regression test log</a> · <a href="{REPO}/blob/main/evidence/browser-smoke.json">Browser check</a></p></section>
<section id="limits"><div class="eyebrow">Failure analysis</div><h2>Useful suggestions have boundaries.</h2><p>{escape(failed[0]['title'])} ranked {failed[0]['rank']} and {escape(failed[1]['title'])} ranked {failed[1]['rank']}, missing the Top-10 target. Coverage ranking can favor shorter recipes sharing fewer but proportionally more ingredients. A future explicit main-ingredient rule needs testing against a broader independent set.</p>
<p>The use-soon boost is a preference, so all top three recipes need not use it. Our mushroom browser example demonstrates this. An explicit must-use filter would be a distinct future feature. Arbitrary typos and Chinese input remain unsupported; source data can omit ingredients, measures or times. {evidence['unknown_time_count']} recipes have unknown time and are excluded when a limit is set.</p>
<p><strong>Food Rescue does not assess freshness or edibility, clear allergens, prescribe diets, or demonstrate reduced food waste.</strong> Keyword checks catch only known patterns. Check packaging and original recipes yourself; missing ingredients and quantities still matter. No dietary or religious certification is provided.</p>
<p>Pantry data remain in the active app session; the app does not write pantry history. Live AI is explicit opt-in and sends the selected title and matched ingredient options. Hosting/provider logs depend on the operator; avoid private or sensitive entries.</p></section>
<section id="run"><div class="eyebrow">Reproduce it</div><h2>Run without a model key.</h2><p>Recorded environment: Python {escape(evidence['python'])} on Windows. From the repository root:</p><pre><code>python -m venv .venv
.\\.venv\\Scripts\\python -m pip install -r requirements-lock.txt
.\\.venv\\Scripts\\python run_local.py</code></pre><p>On macOS/Linux use <code>.venv/bin/python</code>. For a dependency-free offline demo run <code>python run_local.py --cli</code>. The browser opens at the localhost URL printed by Streamlit.</p>
<pre><code>python -m unittest discover -s tests -v
python src/mcp_server.py --test
python benchmark.py --repeats 3
python scripts/evaluate.py</code></pre><p>Run tests using your installed environment's Python. <a href="{REPO}#readme">Complete README</a> · <a href="{REPO}/blob/main/docs/REPRODUCIBILITY.md">Reproduction and hosting notes</a></p>
<h3>Data and attribution</h3><p>The fixed CSV preserves 59 seed recipes and expands to 1,018 unique titles using the public <a href="https://www.kaggle.com/datasets/thedevastator/better-recipes-for-a-better-life">Recipes Dataset</a> export. Catalogue metadata lists CC0: Public Domain. Per-recipe Allrecipes links are retained; underlying recipe rights and recipe safety were not independently audited. <a href="{REPO}/blob/main/data/provenance.json">Source URLs, licence record and checksums</a>.</p>
<p class="muted">Recorded evaluation: {escape(evidence['generated_at_utc'])}. This page displays real saved evidence. The repository includes scripts to rerun it; hosting and the final submitted revision should be verified separately.</p></section>
</main><footer>Food Rescue · Group 40 · AILT9019. AI assisted development and documentation; the report records disclosure, verification and individual contributions. Public page omits private contribution details.</footer></body></html>'''
    (ROOT / "docs/index.html").write_text(html, encoding="utf-8")
    (ROOT / "docs/.nojekyll").touch()
    notes = f'''# Evaluation results

Generated from `evidence/evaluation.json` at {evidence['generated_at_utc']}.

| Measure | Observed |
| --- | --- |
| Known-item Top-10 hits | {s['top10_hits']}/{s['retrieval_total']} (80%) |
| Normalization exact matches | {s['normalization_correct']}/{s['normalization_total']} (93.3%) |
| Refusal contract | {s['refusals_passed']}/{s['refusals_total']} |
| Time-filter queries | {s['time_queries_passed']}/{s['time_queries_total']}; {s['timed_recipes_checked']} returned recipes checked |
| Three cold shared-service searches | max {s['cold_max_seconds']:.3f} s |
| Three warm shared-service searches | median {s['warm_median_seconds']:.3f} s |

{evidence['method']}

The target is present in the bundled CSV, and a hit means its exact title appears at ranks 1-10 for the fixed query. With one designated target per query, this is a known-item hit rate, corresponding to the proposal's Top-10 recall criterion. This small, manually selected set is not a measure of general user satisfaction. Seven cases are chicken-focused; independent broader sampling would improve it.

Observed misses: Chicken Stir-Fry ranked {failed[0]['rank']}; Apple Crisp ranked {failed[1]['rank']}. Simple coverage promotes shorter recipes. Normalization fails `chikcen` and Chinese broccoli because arbitrary spell correction and translation are absent. Unknown inputs can still resemble arbitrary English keys; keyword guards are a limited defensive layer, not edibility classification.

Use-soon scenarios 5-6 in the original benchmark use small synthetic fixtures. They prove the weight rule in those fixtures, not that every real-corpus Top-3 contains a use-soon item. The actual mushroom preset shows the stronger proposal guarantee is not met. Improving this requires an explicit must-use option and evaluation of its tradeoff with coverage.

Timing includes in-process shared validation/loading/ranking/payload construction. It excludes browser/HTTP/network and live AI. The cold cache is cleared before each cold sample; first interpreter startup is not timed. Regression tests simulate provider successes, timeout and invalid content. No live model quality/latency was measured. Source times are estimates; {evidence['unknown_time_count']} unknown-time recipes are excluded under a time cap. See raw case-level JSON, benchmark/test logs and browser smoke evidence for practical limits.
'''
    (ROOT / "docs/EVALUATION.md").write_text(notes, encoding="utf-8")
    print("Built docs/index.html and docs/EVALUATION.md from recorded evidence")


if __name__ == "__main__":
    main()
