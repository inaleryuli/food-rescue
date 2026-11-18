# Evaluation results

Generated from `evidence/evaluation.json` at 2026-11-17T10:53:55.116822+00:00.

| Measure | Observed |
| --- | --- |
| Known-item Top-10 hits | 8/10 (80%) |
| Normalization exact matches | 28/30 (93.3%) |
| Refusal contract | 11/11 |
| Time-filter queries | 30/30; 243 returned recipes checked |
| Three cold shared-service searches | max 0.272 s |
| Three warm shared-service searches | median 0.022 s |

Small, explicit known-item convenience set: three core ingredients per recipe, no time limit; target title must appear in the first 10. Includes broad queries expected to expose coverage-ranking limitations. Not a held-out user study.

The target is present in the bundled CSV, and a hit means its exact title appears at ranks 1-10 for the fixed query. With one designated target per query, this is a known-item hit rate, corresponding to the proposal's Top-10 recall criterion. This small, manually selected set is not a measure of general user satisfaction. Seven cases are chicken-focused; independent broader sampling would improve it.

Observed misses: Chicken Stir-Fry ranked 16; Apple Crisp ranked 28. Simple coverage promotes shorter recipes. Normalization fails `chikcen` and Chinese broccoli because arbitrary spell correction and translation are absent. Unknown inputs can still resemble arbitrary English keys; keyword guards are a limited defensive layer, not edibility classification.

Use-soon scenarios 5-6 in the original benchmark use small synthetic fixtures. They prove the weight rule in those fixtures, not that every real-corpus Top-3 contains a use-soon item. The actual mushroom preset shows the stronger proposal guarantee is not met. Improving this requires an explicit must-use option and evaluation of its tradeoff with coverage.

Timing includes in-process shared validation/loading/ranking/payload construction. It excludes browser/HTTP/network and live AI. The cold cache is cleared before each cold sample; first interpreter startup is not timed. Regression tests simulate provider successes, timeout and invalid content. No live model quality/latency was measured. Source times are estimates; 41 unknown-time recipes are excluded under a time cap. See raw case-level JSON, benchmark/test logs and browser smoke evidence for practical limits.
