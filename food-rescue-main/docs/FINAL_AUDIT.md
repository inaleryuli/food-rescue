# Final-product audit

Reviewed against the supplied final rubric, revised proposal, report template and exported Week Two action-plan conversation. Deadline: **20 November 2026, 23:59 UTC+8**. No external publishing, commits, pushes, messages or Moodle uploads were performed in this review.

## Completed locally

| Requirement or gap | Final artifact/evidence |
| --- | --- |
| One actual core workflow across interfaces | `src/service.py`, `src/validation.py`; browser, CLI and MCP use the same engine |
| Stale root/src implementations | Root modules are compatibility imports; alias improvements retained in `src/normalizer.py` |
| >25 ingredient refusal failed at baseline | Shared validation fixes it; regression covers engine, CLI agent and MCP |
| Safety/scope and invalid data | Raw pantry/use-soon hazards, spoilage/medical/allergen keywords, staples, size/time/type checks; explicit no-match and unavailable-data responses |
| Dataset expansion and provenance | 1,018 titles, fixed source-unit parsing, source quantities/servings/URLs, preserved 59 seed rows and SHA-256 provenance |
| Use-soon, time filter and transparent results | Weighted 1.5/0.5/1.0 coverage, hard known-time filter, top three cards, missing list and original instructions |
| Shopping-list milestone | Per-recipe `.txt` download, checked through real browser execution |
| Agent/UI connection | Offline explanation plus explicit opt-in live ingredient highlight; invalid output/timeouts fall back visibly |
| Quantitative quality evidence | `scripts/evaluate.py`, fixed raw cases, per-case retrieval/normalization/refusal/time results and timestamps/hashes |
| Reproducibility | Pinned direct dependencies and full lock; setup/run/test documentation and clean source-copy check |
| Public-page content | `docs/index.html` with method, team-built features, source/setup, actual results, real run, failure cases and limitations |
| Report and submission handoff | Locally generated review report, four-person checklist/scripts, real-link configuration, validator/ZIP builder |

## Explicit final-scope decisions

- Keep the fixed CSV, regex/alias normalizer and deterministic ranking. PostgreSQL, Redis, spaCy, vector retrieval and a separate HTTP backend remain deferred. Caching is in-process. The existing midterm implementation already used this simpler architecture; the final report must describe it accurately.
- Return three cards, with Top-10 available to evaluation. Do not claim a 100-result dashboard.
- Keep the proposal's weighted scoring. The boost does **not guarantee** all three winners contain a use-soon item; a real mushroom preset can still rank a non-mushroom recipe higher. This is an observed limitation, not evidence that the stronger proposal criterion passed on the whole dataset. A future must-use constraint would need its own explicit product rule and tests.
- Narrow optional AI to choosing an existing ingredient for an explanation. Free-form substitutions and AI-written cooking steps were removed to preserve source facts. No model is required to run or grade the core workflow.
- Do not add a dietary filter that could imply allergen, medical or religious certification without reliable labels.
- Measure recommendation behaviour, not actual food-waste reduction. Timings are local shared-service calls; the original API/browser/LLM SLAs have not been established.

## Still requires the group

The local application is ready for review and recording. Submission readiness additionally requires publishing and checking the webpage/app with the group's accounts, recording two real videos, confirming actual contributions and AI-use verification, exporting/reading the final report PDF (five pages maximum), testing the committed revision from a fresh clone, and uploading the final ZIP. See `submission/CHECKLIST.md`; unresolved URLs are deliberately blank rather than fabricated.
