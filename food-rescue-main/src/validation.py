"""Shared, offline input contract for the browser, CLI, engine and MCP tool."""

import re
import unicodedata

from .normalizer import normalize_ingredient, normalize_pantry

MAX_PANTRY_INGREDIENTS = 25
DANGEROUS_NON_FOOD = (
    "bleach", "soap", "detergent", "motor oil", "battery", "shampoo",
    "cleaner", "plastic", "metal", "glass", "antifreeze", "pesticide",
    "disinfectant", "petrol", "gasoline", "rat poison",
)
_HAZARDS = re.compile(r"\b(?:" + "|".join(map(re.escape, DANGEROUS_NON_FOOD)) + r")\b", re.I)
_OUT_OF_SCOPE = re.compile(
    r"\b(?:mold(?:y)?|mould(?:y)?|spoiled|spoiling|rotten|expired|edibility|"
    r"allerg\w*|anaphylaxis|diabet\w*|clinical|therapeutic|medical|"
    r"food poisoning|safe to (?:eat|cook)|still safe|safe for|eat after|"
    r"left out|smells? (?:bad|sour|off)|kidney disease|renal diet)\b", re.I,
)


class InputError(ValueError):
    def __init__(self, message, reason="invalid_input"):
        super().__init__(message)
        self.reason = reason


def as_items(value, name="pantry"):
    if value is None:
        return []
    if isinstance(value, str):
        value = [value]
    try:
        items = list(value)
    except TypeError as error:
        raise InputError(f"{name} must be a list of ingredient strings.") from error
    if any(not isinstance(item, str) for item in items):
        raise InputError(f"{name} must contain only strings.")
    return [" ".join(item.split()) for item in items if item.strip()]


def check_safety(items):
    """A limited keyword guard, never an edibility or allergen classifier."""
    for item in items:
        normalized = unicodedata.normalize("NFKC", item).replace("-", " ")
        if _HAZARDS.search(normalized):
            raise InputError(
                f"[SAFETY REFUSAL] Dangerous non-food item detected: '{item}'. "
                "Food Rescue only processes safe, edible ingredients.", "non_food",
            )
    for item in items:
        if _OUT_OF_SCOPE.search(item):
            raise InputError(
                "[SCOPE REFUSAL] Food Rescue cannot assess spoilage, edibility, "
                "medical diets or allergen safety. Ask a qualified professional "
                "or consult official food-safety guidance.", "out_of_scope",
            )


def validate_request(pantry, use_soon=(), max_time=None):
    raw = as_items(pantry)
    soon_raw = as_items(use_soon, "use_soon")
    check_safety(raw + soon_raw)
    if len(raw) > MAX_PANTRY_INGREDIENTS or len(soon_raw) > MAX_PANTRY_INGREDIENTS:
        raise InputError("Overload on ingredients: please provide no more than 25 ingredients.", "overload")
    if any(len(item) > 200 for item in raw + soon_raw):
        raise InputError("Each ingredient must be at most 200 characters.")
    if max_time is not None and (
        isinstance(max_time, bool) or not isinstance(max_time, int) or max_time < 1
    ):
        raise InputError("max_time must be a positive whole number of minutes.")
    # Do not silently discard unsupported scripts or quantity-only entries.
    if any(not normalize_ingredient(item) for item in raw + soon_raw):
        raise InputError("Enter an English ingredient name, not just a quantity.")
    try:
        clean = normalize_pantry(raw)
    except ValueError as error:
        raise InputError(str(error), "staples_only") from error
    soon = list(dict.fromkeys(normalize_ingredient(item) for item in soon_raw))
    if any(item not in clean for item in soon):
        raise InputError("Use-soon ingredients must also be in your pantry.")
    return clean, soon, max_time
