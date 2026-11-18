"""Food Rescue CLI: python -m src.app (or python src/app.py)."""
import argparse
import json
import sys
from pathlib import Path

if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from src.agent import run_food_rescue
from src.service import search_food_rescue


def main(argv=None):
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--pantry", nargs="+", default=["chicken breast", "broccoli", "garlic", "soy sauce"])
    parser.add_argument("--use-soon", nargs="*", default=[])
    parser.add_argument("--max-time", type=int, default=40)
    parser.add_argument("--json", action="store_true", help="Print the structured search response")
    parser.add_argument("--ai", action="store_true", help="Opt in to a live ingredient highlight, if configured")
    args = parser.parse_args(argv)
    if args.json:
        payload = search_food_rescue(args.pantry, args.use_soon, args.max_time)
        print(json.dumps(payload, ensure_ascii=False, indent=2))
    else:
        print(run_food_rescue(args.pantry, args.use_soon, args.max_time, use_ai=args.ai))


if __name__ == "__main__":
    main()
