"""Check AI configuration safely; --live makes one explicit provider request."""
import argparse
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--live", action="store_true")
    args = parser.parse_args()
    from dotenv import load_dotenv
    load_dotenv(ROOT / ".env")
    missing = [name for name in ("BAILIAN_API_KEY", "BAILIAN_BASE_URL", "BAILIAN_MODEL")
               if not os.getenv(name, "").strip() or os.getenv(name, "").startswith("your_")]
    if missing:
        print("Missing configuration: " + ", ".join(missing) + ". See README.md. No request made.")
        return 1
    print("All three AI settings are present. Credential values are hidden.")
    if not args.live:
        print("No request made. Use --live to verify one actual provider response.")
        return 0
    from src.agent import explain_recipe
    from src.service import search_food_rescue
    recipe = search_food_rescue(["egg", "rice"])["recipes"][0]
    result = explain_recipe(recipe, use_ai=True)
    print("mode: " + result["mode"])
    print(result["status"])
    return 0 if result["mode"] == "live_ai" else 1


if __name__ == "__main__":
    raise SystemExit(main())
