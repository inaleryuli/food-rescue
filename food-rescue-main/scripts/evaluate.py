"""Write actual quality, constraint and latency evidence: python scripts/evaluate.py."""
import argparse
import hashlib
import json
import platform
import statistics
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from src.engine import load_recipes, rank_recipes, _load_recipes_cached, _matches
from src.normalizer import normalize_ingredient
from src.service import search_food_rescue


def evaluate(repeats=3):
    cases = json.loads((ROOT / "data/evaluation_cases.json").read_text(encoding="utf-8"))
    normalized = [{"input": raw, "expected": expected, "observed": normalize_ingredient(raw),
                   "passed": normalize_ingredient(raw) == expected} for raw, expected in cases["normalization"]]
    retrieval = []
    durations = []
    for case in cases["retrieval"]:
        start = time.perf_counter()
        ranked = rank_recipes(case["pantry"], limit=100)
        durations.append(time.perf_counter() - start)
        rank = next((i for i, recipe in enumerate(ranked, 1) if recipe["title"] == case["title"]), None)
        retrieval.append({**case, "rank": rank, "top10_hit": rank is not None and rank <= 10})
    refusals = []
    for case in cases["refusals"] + [{"pantry": [f"ingredient {i}" for i in range(26)], "reason": "overload"}]:
        result = search_food_rescue(case["pantry"], case.get("use_soon"))
        refusals.append({"input": case, "observed_reason": result.get("reason"),
                         "passed": result["status"] == "refused" and result.get("reason") == case["reason"]})
    constraints = []
    for case in cases["retrieval"]:
        for minutes in (15, 30, 45):
            result = search_food_rescue(case["pantry"], max_time=minutes, limit=10)
            constraints.append({"pantry": case["pantry"], "max_time": minutes, "count": result["count"],
                                "passed": all(r["time_minutes"] is not None and r["time_minutes"] <= minutes for r in result["recipes"])})
    # Clear data and matching caches before each first-call sample.
    cold = []
    warm = []
    for _ in range(repeats):
        _load_recipes_cached.cache_clear()
        _matches.cache_clear()
        start = time.perf_counter()
        search_food_rescue(["chicken breast", "broccoli", "garlic", "soy sauce"], ["broccoli"], 40)
        cold.append(time.perf_counter() - start)
        start = time.perf_counter()
        search_food_rescue(["chicken breast", "broccoli", "garlic", "soy sauce"], ["broccoli"], 40)
        warm.append(time.perf_counter() - start)
    sample = search_food_rescue(["chicken breast", "mushroom", "butter", "flour"], ["mushroom"], 30)
    recipes = load_recipes()
    code_files = sorted([*(ROOT / "src").glob("*.py"), ROOT / "streamlit_app.py",
                         ROOT / "scripts/import_recipe_dataset.py", ROOT / "data/evaluation_cases.json"])
    summary = {
        "normalization_correct": sum(r["passed"] for r in normalized), "normalization_total": len(normalized),
        "top10_hits": sum(r["top10_hit"] for r in retrieval), "retrieval_total": len(retrieval),
        "refusals_passed": sum(r["passed"] for r in refusals), "refusals_total": len(refusals),
        "time_queries_passed": sum(r["passed"] for r in constraints), "time_queries_total": len(constraints),
        "timed_recipes_checked": sum(r["count"] for r in constraints),
        "cold_max_seconds": max(cold), "warm_median_seconds": statistics.median(warm),
    }
    return {
        "generated_at_utc": datetime.now(timezone.utc).isoformat(), "python": platform.python_version(),
        "platform": platform.platform(), "dataset_sha256": hashlib.sha256((ROOT / "data/sample_recipes.csv").read_bytes()).hexdigest(),
        "code_sha256": hashlib.sha256(b"".join(p.read_bytes() for p in code_files)).hexdigest(),
        "code_files": {p.relative_to(ROOT).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest() for p in code_files},
        "dataset_count": len(recipes), "unknown_time_count": sum(r["time_minutes"] is None for r in recipes),
        "method": cases["method"], "summary": summary, "normalization": normalized, "retrieval": retrieval,
        "refusals": refusals, "constraints": constraints, "latency": {"cold_seconds": cold, "warm_seconds": warm,
        "scope": "In-process shared service including validation, CSV loading, scoring and response construction; excludes HTTP/browser/network and live LLM. No live model request performed."},
        "real_run_example": sample,
        "passed": summary["top10_hits"] / summary["retrieval_total"] >= 0.8 and all(r["passed"] for r in refusals + constraints) and max(cold + warm) < 1.5,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=ROOT / "evidence/evaluation.json")
    parser.add_argument("--repeats", type=int, default=3)
    args = parser.parse_args()
    if args.repeats < 1:
        parser.error("repeats must be positive")
    result = evaluate(args.repeats)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result["summary"], indent=2))
    print("PASS" if result["passed"] else "FAIL", "- details:", args.output)
    return 0 if result["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
