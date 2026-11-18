# Two separate final videos

Use the rubric's final-video requirements, not the old one-minute midterm script. Name labels must be visible in the Zoom presentation. All four members speak. Rehearse with a timer; target 2:40-2:50 total. Replace future/unfinished claims before recording.

## Presentation: suggested 2:45 Zoom script

**0:00-0:40 — HU, Chengli, problem and final scope**

“We are Group 40. Food Rescue helps students answer: what can I cook with the ingredients already in my kitchen? Users enter a pantry list, mark ingredients to use soon, and set a cooking-time limit. We recommend existing recipes and show missing items. Our final version uses a fixed CSV and a shared Python service so it works without accounts or API keys. It does not assess freshness, medical diets or allergen safety.”

**0:40-1:20 — YU, Wei, method and customisation**

“We built ingredient normalization, regional aliases, weighted matching and the input guards. For example, scallions map to green onion. Recipes over the time limit are excluded. We score available ingredient weight divided by total recipe weight: use-soon items weigh 1.5, staples 0.5, and other ingredients 1.0. We preserve original recipe instructions and show source quantities and links. The fixed dataset has 1,018 titles. A coverage score still does not guarantee a complete meal.”

**1:20-2:00 — SIDARTA, Owen, evidence and limitations**

“Our automated suite and live browser check exercise the real workflow, shopping-list downloads, refusal cases and service failures. On our small known-item evaluation, eight of ten intended recipes appeared in the top ten. Normalization matched 28 of 30 reference strings. All eleven refusal cases and thirty cooking-time queries passed. Two broad queries missed their target recipes because shorter recipes can score higher. Typo and Chinese input remain unsupported. Search timing is measured locally, not as an internet or live-model guarantee.”

**2:00-2:45 — LO, Si Ching, user workflow and team work**

“The browser provides presets, manual pantry editing, use-soon checkboxes and recipe cards with shopping-list downloads. Our optional AI explanation can only select a matched ingredient to highlight; it cannot change temperatures or recipe steps and it falls back if unavailable. The separate demo shows continuous execution, tests and a refusal. Earlier work was divided across engine and agent access, data and normalization, evaluation, and the interface. We have documented the actual final contributions and checks in the report. This is a meal-suggestion tool; we have not demonstrated a reduction in food waste.”

Only say “we have documented” after the group finishes that record. Show the actual current test count/results on screen; update the script if the evidence changes.

## Demo: suggested 5-7 minutes, no rubric length limit

1. Start a continuous screen capture with terminal and browser visible. Show the final commit and `python --version`. Do not expose `.env`, student IDs, emails, notifications or provider keys.
2. Run `python run_local.py`, open the printed localhost URL and click a preset. Show recognized pantry, time limit, scores, matched/missing ingredients and original instructions. Say these are retrieved source instructions, not generated recipes.
3. Add/edit a raw ingredient such as `2 large eggs`; toggle use-soon and change time. Explain the weight formula and hard filter. Show that suggestions may still require shopping and do not guarantee use-soon in every winner.
4. Download a shopping list and open the text file. Open or display the original source link and available ingredient measures.
5. Show the offline explanation. If showing an unconfigured live-AI option, state that the displayed result is fallback. Do not call a mock or deterministic explanation a live model response.
6. Clear the pantry and enter `bleach`; show the refusal and absence of cards. Optionally repeat with only salt/water or a spoilage question. Show `python -m src.app --pantry unobtainium --json` for a real no-match boundary.
7. Run `python -m unittest discover -s tests -v`, `python src/mcp_server.py --test`, and `python scripts/evaluate.py`. Show the actual output and open `evidence/evaluation.json`: 8/10 retrieval, 28/30 normalization, refusal/time results, the failed target ranks and the timing scope. Explain the use-soon synthetic fixtures separately from real-CSV evidence.
8. Finish on the public project page/repository. State remaining limitations: English vocabulary, incomplete source data, limited keyword safety, coverage bias, no verified food-waste outcome, and no live-LLM SLA.

Use readable zoom, clear audio and captions/transcript. If a setup or test fails during recording, fix it and record again; do not edit separate executions to imply one uninterrupted successful run.
