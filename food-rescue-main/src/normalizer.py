"""Small, deterministic English ingredient normalizer; no model/download needed.

One string represents one ingredient. Preparation adjectives, quantities and
measurement units are removed, while food/product names (e.g. brown rice,
chicken broth and garlic powder) are retained. This is a rule-based baseline,
not an exhaustive food vocabulary or a safety classifier.
"""

import re
import unicodedata
from typing import Iterable, List

_UNITS = {
    "cup", "cups", "tablespoon", "tablespoons", "tbsp", "teaspoon",
    "teaspoons", "tsp", "gram", "grams", "g", "kilogram", "kilograms",
    "kg", "milligram", "milligrams", "mg", "ounce", "ounces", "oz",
    "pound", "pounds", "lb", "lbs", "milliliter", "milliliters", "ml",
    "liter", "liters", "litre", "litres", "l", "pinch", "pinches",
    "clove", "cloves", "can", "cans", "package", "packages",
}
_PREPARATION = {
    "fresh", "large", "medium", "small", "finely", "roughly", "thinly",
    "chopped", "diced", "sliced", "minced", "grated", "shredded", "peeled",
    "beaten", "melted", "softened", "drained", "rinsed", "divided", "skinless", "boneless",
}
# Explicit mappings avoid corrupting words such as asparagus and couscous.
_PLURALS = {
    "eggs": "egg", "tomatoes": "tomato", "potatoes": "potato",
    "onions": "onion", "carrots": "carrot", "mushrooms": "mushroom",
    "peppers": "pepper", "breasts": "breast", "beans": "bean",
    "lentils": "lentil", "peas": "pea", "leaves": "leaf",
    "scallions": "scallion", "courgettes": "courgette",
    "aubergines": "aubergine", "capsicums": "capsicum",
    "chickpeas": "chickpea", "prawns": "prawn",
    "confectioners": "confectioner",
}
# Phrase-level aliases cover common regional and culinary names. Keys and
# values use singular tokens so they can be applied after plural handling.
_ALIASES = {
    ("scallion",): ("green", "onion"),
    ("spring", "onion"): ("green", "onion"),
    ("courgette",): ("zucchini",),
    ("aubergine",): ("eggplant",),
    ("capsicum",): ("bell", "pepper"),
    ("chick", "pea"): ("chickpea",),
    ("garbanzo", "bean"): ("chickpea",),
    ("rocket",): ("arugula",),
    ("prawn",): ("shrimp",),
    ("coriander", "leaf"): ("cilantro",),
    ("caster", "sugar"): ("superfine", "sugar"),
    ("icing", "sugar"): ("powdered", "sugar"),
    ("confectioner", "sugar"): ("powdered", "sugar"),
    ("corn", "starch"): ("cornstarch",),
    ("cornflour",): ("cornstarch",),
}
_STAPLES = {"salt", "pepper", "water", "oil"}
_STAPLE_QUALIFIERS = {
    "ground", "black", "white", "sea", "coarse", "fine", "kosher", "table",
    "olive", "vegetable", "canola", "corn", "sesame", "peanut", "cooking",
    "extra", "virgin", "light", "hot", "cold", "warm", "boiling",
    "lukewarm", "filtered", "tap",
}


def normalize_ingredient(raw: str) -> str:
    """Return a canonical ingredient key, or an empty string for quantity only.

    Measurement units are stripped only after a quantity so food names such
    as ``pound cake`` survive. Compound product names remain separate keys.
    """
    if not isinstance(raw, str):
        raise TypeError("Each ingredient must be a string.")
    text = unicodedata.normalize("NFKC", raw).lower().replace("⁄", "/")
    text = re.sub(r"\b(?:to taste|as needed)\b", " ", text)
    # Tokenize numbers as well as words to distinguish '1 pound' from cake.
    tokens = re.findall(r"\d+(?:[./]\d+)*|[a-z]+", text)
    result = []
    quantity_seen = False
    for token in tokens:
        if token[0].isdigit():
            quantity_seen = True
            continue
        if quantity_seen and token in _UNITS:
            continue
        if token in _PREPARATION:
            continue
        result.append(_PLURALS.get(token, token))
        quantity_seen = False
    if result and result[-1] == "egg":
        result = [word for word in result if word not in {"brown", "white"}]
    return " ".join(_canonicalize_aliases(result))


def _canonicalize_aliases(words: List[str]) -> List[str]:
    """Replace known ingredient synonyms, preferring the longest phrase."""
    aliases = sorted(_ALIASES.items(), key=lambda item: len(item[0]), reverse=True)
    canonical = []
    index = 0
    while index < len(words):
        for alias, replacement in aliases:
            end = index + len(alias)
            if tuple(words[index:end]) == alias:
                canonical.extend(replacement)
                index = end
                break
        else:
            canonical.append(words[index])
            index += 1
    return canonical


def canonicalize_ingredient_tokens(tokens: Iterable[str]) -> List[str]:
    """Apply ingredient aliases to already-tokenized matching input."""
    return _canonicalize_aliases(list(tokens))


def normalize_pantry(items: Iterable[str]) -> List[str]:
    """Normalize and deduplicate entries in order; reject an empty/staples pantry.

    Pass a list for multiple ingredients; a single string is one ingredient.
    Safety checks for non-food or spoiled food belong to the safety agent.
    """
    if isinstance(items, str):
        items = [items]
    normalized = list(dict.fromkeys(
        key for item in (() if items is None else items)
        if (key := normalize_ingredient(item))
    ))
    if not normalized or all(_is_staple(key) for key in normalized):
        raise ValueError("Please provide at least one core ingredient.")
    return normalized


def _is_staple(key: str) -> bool:
    core = [word for word in key.split() if word not in _STAPLE_QUALIFIERS
            and word not in {"and", "or"}]
    return bool(core) and all(word in _STAPLES for word in core)
