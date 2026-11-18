"""One search response contract, shared by every product entry point."""

from .engine import rank_recipes
from .validation import InputError, validate_request


def search_food_rescue(pantry, use_soon=None, max_time=None, limit=3):
    try:
        clean, soon, minutes = validate_request(pantry, use_soon, max_time)
        recipes = rank_recipes(clean, soon, minutes, limit=limit)
    except InputError as error:
        message = str(error)
        if not message.startswith("["):
            message = "[INPUT ERROR] " + message
        return {"status": "refused", "reason": error.reason, "message": message, "count": 0, "recipes": []}
    except OSError:
        return {"status": "error", "reason": "dataset_unavailable", "message": "The recipe dataset could not be loaded. Check data/sample_recipes.csv.", "count": 0, "recipes": []}
    query = {"pantry": clean, "use_soon": soon, "max_time": minutes}
    message = ""
    if not recipes:
        message = "No recipes share a main ingredient with your pantry"
        if minutes is not None:
            message += f" within {minutes} minutes"
        message += ". Try different ingredients or more time."
    return {"status": "ok" if recipes else "no_matches", "message": message,
            "query": query, "count": len(recipes), "recipes": recipes}
