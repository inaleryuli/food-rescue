#!/usr/bin/env python3
"""Merge the public Allrecipes export into Food Rescue's CSV format.

The input is the ``recipes.csv`` file from the Kaggle "Recipes Dataset"
(https://www.kaggle.com/datasets/thedevastator/better-recipes-for-a-better-life).
An accessible mirror is documented at
https://github.com/SamShtram/Cmpsc441_Intelligent_Recipe_Recommendation_System.

The project's original recipes are retained. New rows are added once per
case-insensitive title, with ingredient lists converted to the Python-literal
format expected by ``src.engine``.
"""

import argparse
import csv
import re
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT = PROJECT_ROOT / "data" / "sample_recipes.csv"
OUTPUT_FIELDS = [
    "Row", "Name", "Prep Time", "Cook Time", "Total Time", "Servings",
    "Yield", "Ingredients", "Directions", "url", "Additional Time",
]

# Split only at commas followed by a new measured ingredient. This keeps
# commas inside notes such as "peeled, cored and sliced" with their ingredient.
_FRACTIONS = "½⅓⅔¼¾⅛⅜⅝⅞⅙⅚"
_AMOUNT = rf"(?:\d+\s+\d+/\d+|\d+/\d+|\d+(?:\.\d+)?(?:\s*[{_FRACTIONS}])?|[{_FRACTIONS}])"
_NEXT_INGREDIENT = re.compile(r",\s*(?=" + _AMOUNT + r"\s)")
_MEASURE = re.compile(r"^\s*(?P<quantity>" + _AMOUNT + r")\s*", re.I)
_UNIT = re.compile(
    r"^(?P<unit>(?:\([^)]*\)\s*)?(?:cups?|tablespoons?|tbsp|teaspoons?|tsp|"
    r"grams?|g|kilograms?|kg|ounces?|oz|pounds?|lbs?|lb|milliliters?|ml|liters?|litres?|l|"
    r"cloves?|cans?|packages?|slices?|pieces?|stalks?|heads?|bottles?|jars?|packets?|"
    r"envelopes?|sheets?|sticks?|sprigs?|bunches?|loaves?))\b\s*", re.I,
)


def _ingredient_records(raw):
    """Retain source quantities and avoid stripping unit prefixes from food names."""
    records = []
    for part in _NEXT_INGREDIENT.split(raw or ""):
        part = part.strip(" ,;\n\t")
        quantity = unit = ""
        match = _MEASURE.match(part)
        if match:
            quantity = match["quantity"]
            part = part[match.end():]
            measure = _UNIT.match(part)
            if measure:
                unit = measure["unit"]
                part = part[measure.end():]
        if part and not part.lower().startswith(("optional:", "for serving:")):
            records.append({"quantity": quantity, "unit": unit, "name": part})
    return records


def _ingredient_names(raw):
    return [record["name"] for record in _ingredient_records(raw)]


def _directions(raw):
    if not raw:
        return []
    return [line.strip() for line in raw.splitlines() if line.strip()]


def _read_existing(output_path):
    if not output_path.exists():
        return []
    with output_path.open(newline="", encoding="utf-8-sig") as handle:
        return list(csv.DictReader(handle))


def import_dataset(source_path, output_path=DEFAULT_OUTPUT, rebuild=False):
    source_path = Path(source_path)
    output_path = Path(output_path)
    existing = _read_existing(PROJECT_ROOT / "data" / "seed_recipes.csv" if rebuild else output_path)
    seen_titles = {
        (row.get("Name") or "").strip().casefold()
        for row in existing
        if (row.get("Name") or "").strip()
    }
    rows = list(existing)
    next_id = len(rows)

    with source_path.open(newline="", encoding="utf-8-sig") as handle:
        for source in csv.DictReader(handle):
            title = (source.get("recipe_name") or "").strip()
            title_key = title.casefold()
            if not title or title_key in seen_titles:
                continue
            ingredients = _ingredient_records(source.get("ingredients", ""))
            directions = _directions(source.get("directions", ""))
            if not ingredients or not directions:
                continue
            rows.append(
                {
                    "Row": str(next_id),
                    "Name": title,
                    "Prep Time": (source.get("prep_time") or "").strip(),
                    "Cook Time": (source.get("cook_time") or "").strip(),
                    "Total Time": (source.get("total_time") or "").strip(),
                    "Servings": (source.get("servings") or "").strip(),
                    "Yield": (source.get("yield") or "").strip(),
                    "Ingredients": repr(ingredients),
                    "Directions": repr(directions),
                    "url": (source.get("url") or "").strip(),
                    "Additional Time": "",
                }
            )
            seen_titles.add(title_key)
            next_id += 1

    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=OUTPUT_FIELDS, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)
    return len(rows)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source_csv", help="Path to the downloaded recipes.csv")
    parser.add_argument(
        "--output", type=Path, default=DEFAULT_OUTPUT,
        help=f"Destination CSV (default: {DEFAULT_OUTPUT})",
    )
    parser.add_argument("--rebuild", action="store_true", help="Rebuild from the preserved 59 seed recipes, refreshing imported rows")
    args = parser.parse_args()
    print(f"Wrote {import_dataset(args.source_csv, args.output, rebuild=args.rebuild)} recipes to {args.output}")


if __name__ == "__main__":
    main()
