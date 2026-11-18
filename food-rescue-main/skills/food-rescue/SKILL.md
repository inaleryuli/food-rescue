---
name: food-rescue
description: Search the local Food Rescue recipe corpus from pantry ingredients, use-soon choices and a maximum cooking time. Use for pantry-based cooking requests; refuse known hazards, spoilage/medical/allergen clearance and staples-only or overloaded lists.
---

# Food Rescue Recipe Skill

## Purpose

Return up to three existing recipes with weighted coverage, missing ingredients, source directions and provenance. This skill describes how to call the repository's shared Python service; it does not include a model, embedded recipe index or independent execution environment.

## When to use

Use when someone asks what to cook from their pantry or wants to use ingredients soon. Do not use for restaurants, medical diets, edibility/spoilage assessments or allergen clearance. Ask for ingredient names if the pantry is missing or ambiguous. Do not invent substitutions or recipes.

## Input constraints

- One string per ingredient; a single string is one ingredient, not characters. English rules and regional aliases are supported; arbitrary spelling correction, translation and brand interpretation are not.
- At most 25 nonblank pantry entries and 25 use-soon entries. Use-soon entries must normalize to items already in the pantry. Keep raw strings until validation has run.
- Maximum time is a positive whole number of minutes, or absent.
- Shared safety checks run before normalization/recipe lookup. Known hazard keywords in either input list trigger full refusal, including bleach and motor oil. Matching uses normalized word boundaries and hyphens, not arbitrary substring rules. See `src/validation.py` for the complete current guard vocabulary.
- Reject recognized spoilage, medical-diet and allergen-clearance patterns. Keyword guards are limited and do not establish edibility.
- Empty/staples-only pantries are refused. Staples are salt, pepper, water and oil plus common variants; at least one non-staple must also match a recipe.

## Concrete steps

1. Collect raw pantry, use-soon subset and optional minutes. Do not strip hazard words or truncate overloaded lists.
2. Call the shared service from the repository working directory:

```python
from src.service import search_food_rescue
payload = search_food_rescue(raw_pantry, raw_use_soon, max_time)
```

Or use the MCP `search_food_rescue` tool registered in `mcp.json`. Both share the same engine and validation. Core service/MCP need only Python, no key.

3. If `status` is `refused`, `no_matches` or `error`, show its message and stop. Do not produce a recipe from memory. Invalid-input requests may need one clarification.
4. For `ok`, present the returned recipes best first:

```text
### 1. <title> - <score:.0%> match - <time_minutes> min
In Your Kitchen: <matched_ingredients>
Need to Buy: <missing_ingredients, or Nothing - you have everything>
Instructions:
<original instruction lines in original order>
Source: <source_url>
```

Show available `ingredient_details`/`servings` when needed; do not invent quantities. Remind the user to check original sources and allergen packaging. The score is not a freshness or safety rating.

## Matching contract

Normalization strips units/quantities and common preparation words, maps plurals/aliases, and deduplicates. Time limits exclude slow and unknown-time rows. Ingredient weight is 1.5 for use-soon, 0.5 for staples, otherwise 1.0. Score is matched weight / total recipe weight. Ties use most matched ingredients, then title A-Z. A non-staple overlap is required; zero/unrelated matches are dropped. These are suggestions and may require buying main ingredients.

A weight boost is not a guarantee that all three recipes contain a use-soon ingredient. Preserve returned ordering and missing items; do not silently add such a guarantee. No medical/dietary certification, live-model latency or verified food-waste reduction is established.

## Examples

Successful input: pantry `['chicken breast', 'mushroom', 'butter', 'flour']`, use-soon `['mushroom']`, maximum 30. Current fixed CSV leads with Chicken Marsala, score 0.5 and time 30. Other required items remain visible; source instructions are retrieved, not generated. Use the actual service result for full details, since corpus changes can change ranks.

Refusal input: pantry `['chicken', 'bleach']`.

```text
[SAFETY REFUSAL] Dangerous non-food item detected: 'bleach'. Food Rescue only processes safe, edible ingredients.
```

Stop without recipes. Staples-only input returns `[INPUT ERROR] Please provide at least one core ingredient.` An overload returns `[INPUT ERROR] Overload on ingredients: please provide no more than 25 ingredients.`

## Verification

`python src/mcp_server.py --test` checks the local tool/protocol surface. `python -m unittest discover -s tests -v` runs regressions (browser/AI tests need installed dependencies). External coding-agent interoperability is a separate client check; do not claim it occurred solely because this skill file exists.
