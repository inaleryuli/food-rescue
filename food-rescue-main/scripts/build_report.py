"""Create a clearly labelled report review copy, using real evaluation evidence.

Pass --template to reuse the course DOCX's styles/section requirements. Generated
review files are local only. Human contributions, final links and PDF sign-off
must be completed by the team before naming a submission report.pdf.
"""
import argparse
import json
from html import escape
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

TITLES = [
    "1. Background", "2. Project pipeline and domain customisation",
    "3. Evaluation and test results", "4. Reproducibility, failure cases and limitations",
    "5. Ethics and AI-use disclosure", "6. Individual contributions by report section", "7. References",
]
REQUIREMENTS = [
    "Who is this for, what problem does it address, why does it matter, and who or what is it not for? State the final scope and any important change from the proposal.",
    "Explain the actual input → processing → output path. Distinguish what your team built from existing model/API/framework capabilities. Describe at least one substantive domain customisation and connect a design choice to a domain need and implementation evidence. A pipeline diagram is encouraged.",
    "State a task-aligned evaluation question or success criterion, test data/cases and method. Report actual quantitative or qualitative results with checkable evidence. Include at least one failure, boundary or safety-refusal case; compare expected and observed behaviour. A compact results table is welcome.",
    "Briefly explain how another person can install, run and test the core path using the README, including safe API setup if needed. Analyse an observed failure and its cause or behaviour; state limitations, scope of applicability and evidence-based improvements. Label cached/mock outputs honestly; never claim these tests were performed if they were not.",
    "Complete all seven AI-use fields below; use ‘none’ where applicable. Name responsible members and describe actual human checks. State data permissions, privacy and project-specific risks.",
    "For every section, list every member and their specific completed work, or ‘none’. Coding and non-coding work count; cite evidence where useful. Include contributions to this statement and references. Also list webpage/video work, team review and any unresolved disagreement.",
    "List cited data sources, external code, models/tools and relevant work in a consistent, traceable format. References count toward the five-page body limit.",
]


def content(evidence):
    s = evidence["summary"]
    return [
        ["Food Rescue supports university students cooking in shared or small kitchens who need meal ideas from ingredients already available. Users supply an English pantry list, optional use-soon items and a cooking-time limit. The final product returns existing recipe cards, missing ingredients, source directions and a downloadable shopping list. It does not assess edibility, prescribe diets, clear allergens or establish reduced food waste.",
         "The original idea came from the team's cooking experience, as recorded in the revised proposal [1]. Compared with that proposal, the final scope retains the CSV/Python architecture adopted at midterm: PostgreSQL, Redis, spaCy, vector search and a separate HTTP API are deferred. Three cards replace the proposed 100-result view. The optional model is restricted to selecting a matched ingredient for an explanation; it cannot generate substitutions or rewrite cooking steps."],
        ["Actual path: pantry + use-soon + minutes → shared safety/scope/type/size checks → regex and alias normalization → fixed CSV/time filter → weighted pantry coverage → deterministic Top-3 cards/JSON → optional validated explanation. The browser, CLI and MCP tool share src/service.py, src/validation.py and src/engine.py. Invalid or unavailable data return clear messages.",
         "The team-built components are normalization/aliases, matching weights, refusal rules, ingestion, browser flow, export, CLI/MCP access and tests. Python and Streamlit supply runtime/interface primitives; the public recipe data supply recipe facts [2–4]. Optional Qwen uses a compatible client [5]; no model is needed for search. A limited 2025-06-18 MCP stdio interface exposes search_food_rescue [6].",
         "Domain customisation: use-soon ingredients weigh 1.5, staples (salt/pepper/water/oil) 0.5 and other ingredients 1.0; score = matched ingredient weight / total recipe weight. Ties use matched count then title. At least one non-staple overlap is required, and unknown or excessive times are excluded under a time limit. Regional aliases map scallion to green onion; raw chicken does not satisfy chicken broth. These rules address pantry entry variation, perishable preference and limited cooking time. Source-backed instructions and validated AI output reduce invented recipe facts; tests and observed failures remain necessary [7]."],
        [f"Evaluation asks whether the fixed workflow normalizes pantry strings, retrieves an intended recipe in the Top-10, enforces time constraints and refuses known invalid cases. data/evaluation_cases.json fixes a small known-item convenience set: ten recipes queried with three core ingredients, 30 normalization strings, eleven refusal cases (including overload) and thirty time-limit queries. Seven retrieval cases are chicken-focused; these are descriptive results, not a held-out user study [7].",
         f"Observed: normalization {s['normalization_correct']}/{s['normalization_total']} (93.3%); Top-10 retrieval {s['top10_hits']}/{s['retrieval_total']} (80%); refusals {s['refusals_passed']}/{s['refusals_total']}; time filters {s['time_queries_passed']}/{s['time_queries_total']} across {s['timed_recipes_checked']} returned recipes. The regression suite passes 45 tests; MCP self-check passes 17 checks. Real local Edge execution verified recipe rendering, a downloaded shopping list, refusal and a mobile viewport. AI integration tests simulate provider success, invalid output and timeout; they do not measure a live model.",
         f"Three cold-cache shared-service searches had maximum {s['cold_max_seconds']:.3f} s; three warm searches had median {s['warm_median_seconds']:.3f} s on Python {evidence['python']} / Windows. Timing includes validation, CSV loading, ranking and payload construction, but excludes interpreter startup, HTTP, browser/network and live AI. It does not establish the proposal's end-to-end API or 3.5-second LLM SLA.",
         "Expected/observed boundaries: bleach and spoilage requests return refusal and zero cards; >25 ingredients now refuse across entry points. Chicken Stir-Fry ranked 16 and Apple Crisp 28, missing the Top-10 target. ‘chikcen’ and Chinese broccoli failed normalization. The original use-soon fixtures pass, but the real mushroom preset can rank a non-mushroom dish first; the stronger all-Top-3 use-soon guarantee was not achieved. The weight rule is a preference."],
        ["README.md gives the pinned environment, installation, browser/CLI launch, optional safe configuration and test commands. Install requirements-lock.txt in a Python 3.14 environment, run python run_local.py, then python -m unittest discover -s tests -v, python src/mcp_server.py --test, python benchmark.py --repeats 3 and python scripts/evaluate.py. Core CLI/MCP work without dependencies or keys. Logs, machine/version data, dataset/code hashes, real case outputs and the clean-source-copy check are in evidence/ [7]. Final remote fresh-clone reproduction remains a team handoff check until this revision is pushed.",
         "Failure analysis: proportional coverage can promote short recipes while missing a longer intended dish; pantry quantities and culinary importance are not modelled. The 1.5 boost cannot force use-soon membership in all three winners. Future improvements are a separately evaluated must-use filter, main-ingredient constraints and a broader independent retrieval benchmark. Rule-based English normalization does not resolve arbitrary brands, typos or translations. Keyword checks cannot classify every unsafe request. Forty-one source rows have unknown time; other source omissions and cooking-time estimates remain. A former unit-prefix importer bug (cantaloupe → taloupe) and stale browser checkbox callback after clear/download were fixed and covered by regression/live-browser checks. No nutritional, safety or environmental outcome is inferred."],
        ["Data and permissions: 59 preserved seed recipes plus a public Allrecipes export produce 1,018 unique titles. The Kaggle catalogue metadata lists CC0: Public Domain; data/provenance.json records source URLs/checksums and processing. Original recipe links are retained for attribution; underlying recipe rights, completeness and safety were not independently audited [2,3].",
         "Privacy and risks: no user accounts or pantry-history files are created. Session pantry entries should not contain personal data. Optional live AI explicitly sends only a selected title and matched ingredient options; provider/hosting retention depends on the operator. .env and secrets.toml are excluded. Persistent notices, shared keyword refusals, visible missing items, source instructions and exact-choice model validation mitigate misinterpretation, allergens and invented steps; they do not establish edibility or medical clearance.",
         "Tools/models used: OpenAI Codex for this final coding/documentation review; the supplied earlier action-plan conversation records Gemini planning. The existing Bailian/Qwen integration is retained as an optional configured provider path; no live model call was made in this final review. Exact earlier model versions require member confirmation; installed client/framework versions are pinned [4,5,7].",
         "Tasks supported: repository/rubric review; code consolidation and fixes; importer repair; tests, measured evaluation, real browser checks; webpage, documentation and report review drafting.",
         "Representative prompts/interactions: the user requested review of the entire workspace against the rubric, proposal and action plan, completion of the final product, and a final four-person submission handoff. The runtime model receives only a constrained ingredient-selection prompt.",
         "Material outputs retained: shared validation/service, fixes in engine/agent/browser/importer, regression and evaluation scripts, webpage, documentation and report review draft; earlier AI-assisted work requires each member's own disclosure.",
         "Verification performed: the coding agent ran the automated suite, MCP subprocess/self-check, measured benchmark/evaluation and actual Edge workflow/download/refusal/mobile checks. These are automated checks. No manual verification by the four members has been established during this session; responsible owners must add their actual checks before submitting.",
         "Known limitations: narrow English rules, limited hazard keywords, incomplete source data, small biased retrieval set, coverage/use-soon limitations and no measured live-model quality/SLA. AI-produced text/code still needs human review.",
         "Team members responsible: HU, Chengli; YU, Wei; SIDARTA, Owen; LO, Si Ching. Their final report contributions, prior AI tools and human verification remain to be confirmed individually. This review copy does not assert their sign-off."],
        ["Member key: A = HU, Chengli; B = YU, Wei; C = SIDARTA, Owen; D = LO, Si Ching. The following is a review record based on commit subjects and the supplied midterm status sheet. It credits completed project work relevant to each section; authorship of this AI-drafted final text and final human verification are not yet confirmed. Each member must correct/approve their entries.",
         "1. Background — A: none verified; B: none verified; C: none verified; D: none verified for this final report section.",
         "2. Pipeline/customisation — A: initial matching engine, agent, repository, skill and MCP (4ea85c7, 4e04b1f, 8dc9c79, 22de2e8); B: normalizer, Top-3 ranking, dataset expansion/aliases (c5ffa69, 85afc9b, 1988376, 99fa0bd); C: none; D: Streamlit interface (a483b35).",
         "3. Evaluation — A: none verified as final human review; B: ranking/normalization regression tests (85afc9b, c5ffa69); C: acceptance scenarios and benchmark (4bcfb38, 2865915); D: none verified for final evaluation. Automated finishing-session results were executed by Codex at A's request, not manually signed off by the group.",
         "4. Reproducibility/limits — A: repository/config/setup documentation (6b8a061, 3f201e0); B: importer and dataset documentation (2e1857a, 7be9469); C: benchmark command (2865915); D: browser setup documentation with interface work (a483b35). Final independent clone check: pending.",
         "5. Ethics/disclosure — A: environment exclusions and refusal/skill rules (f0233fc, d5b12c9, 8dc9c79); B: none verified for final ethics review; C: refusal acceptance tests (4bcfb38); D: browser safety notice (a483b35). All four: prior AI-use/human-check disclosure pending.",
         "6. Contribution statement — A: none verified as human review; B: none; C: none; D: none. Compiled by AI from supplied records; group review and disagreement status are not yet established.",
         "7. References — A: none verified for final reference review; B: dataset/import source documentation (7be9469); C: none; D: none.",
         "Other completed work: C's midterm recording is reported in the supplied status sheet; this is not the final video. D built the browser app. Final public hosting, presentation speaking, video recording/editing, final human review and upload are not yet verified for any member. Proposed remaining roles are in submission/CHECKLIST.md. No final-team agreement is claimed."],
        ["[1] Group 40. AILT9019 Revised Project Proposal and supplied midterm status/action-plan record (course materials, 2026).",
         "[2] TheDevastator. Recipes Dataset. https://www.kaggle.com/datasets/thedevastator/better-recipes-for-a-better-life (catalogue licence checked 17 Nov 2026; metadata URL/checksum in data/provenance.json).",
         "[3] SamShtram et al. Public recipe-data mirror, data/recipes.csv. https://github.com/SamShtram/Cmpsc441_Intelligent_Recipe_Recommendation_System . Original Allrecipes URLs retained per row. Used as a data source, not copied application code.",
         "[4] Python 3.14.7; Streamlit 1.67.0. https://docs.python.org/3/ ; https://docs.streamlit.io/ . Versions in requirements-lock.txt.",
         "[5] Alibaba Cloud Model Studio, compatible chat interface. https://help.aliyun.com/en/model-studio/compatibility-of-openai-with-dashscope . Optional provider model configured by operator; no live run measured.",
         "[6] Model Context Protocol, 2025-06-18 lifecycle/stdio specification. https://modelcontextprotocol.io/specification/2025-06-18/basic/lifecycle .",
         "[7] Group 40, Food Rescue source and generated run evidence. https://github.com/rodri-hu-cl/food-rescue ; evidence/evaluation.json, tests.txt, benchmark.txt, browser-smoke.json, reproduction.txt. Finishing-session AI tool: OpenAI Codex. Evidence reflects the local reviewed revision until pushed."],
    ]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--template", type=Path)
    args = parser.parse_args()
    from docx import Document
    from docx.shared import Inches, Pt, RGBColor
    evidence = json.loads((ROOT / "evidence/evaluation.json").read_text(encoding="utf-8"))
    links = json.loads((ROOT / "submission/links.json").read_text(encoding="utf-8"))
    sections = content(evidence)
    requirements = list(REQUIREMENTS)
    titles = list(TITLES)
    if args.template:
        source = Document(args.template)
        paragraphs = source.paragraphs
        for i, paragraph in enumerate(paragraphs):
            for j, title in enumerate(TITLES):
                # The template calls Section 5 simply Ethics and AI-use disclosure or Ethics.
                if paragraph.text.startswith(f"{j + 1}. ") and not paragraph.text.startswith("e.g."):
                    titles[j] = paragraph.text
                    if i + 1 < len(paragraphs):
                        requirements[j] = paragraphs[i + 1].text
        document = source
        for element in list(document.element.body):
            if not element.tag.endswith("sectPr"):
                document.element.body.remove(element)
    else:
        document = Document()
    for section in document.sections:
        section.top_margin = section.bottom_margin = Inches(.58)
        section.left_margin = section.right_margin = Inches(.65)
        section.page_width, section.page_height = Inches(8.27), Inches(11.69)
    normal = document.styles["Normal"]
    normal.font.name = "Calibri"
    normal.font.size = Pt(9)
    normal.paragraph_format.space_after = Pt(4)
    normal.paragraph_format.line_spacing = 1.05
    document.add_heading("Food Rescue — Final Report", 0)
    document.add_paragraph("REVIEW COPY: complete links, human checks and member sign-off before submission.")
    identity = f"Group 40 · Food Rescue: AI-Assisted Recipe Recommendation · Repository: {links['repository']}"
    public = " · ".join(f"{label}: {links.get(key) or 'Pending team publication/recording'}" for key, label in (("public_webpage", "Public webpage"), ("presentation_youtube", "Presentation"), ("demo_youtube", "Demo")))
    document.add_paragraph(identity)
    document.add_paragraph(public)
    markdown = ["# Food Rescue — report review copy", "", "REVIEW COPY: replace pending human checks/links and confirm contributions before submission.", "", identity, "", public]
    # Four intentionally grouped pages; inspect the exported document/PDF for overflow.
    groups = ((0, 1), (2, 3), (4,), (5, 6))
    html_pages = []
    for page_number, group in enumerate(groups):
        if page_number:
            document.add_page_break()
        parts = []
        if not page_number:
            parts.append(f"<h1>Food Rescue — Final Report</h1><p class='review'>REVIEW COPY · Human sign-off and final links pending</p><p>{escape(identity)}</p><p>{escape(public)}</p>")
        for index in group:
            document.add_heading(titles[index], level=1)
            requirement = document.add_paragraph(requirements[index])
            for run in requirement.runs:
                run.font.color.rgb = RGBColor.from_string("666666")
                run.font.size = Pt(8)
            markdown += ["", "## " + titles[index], "", requirements[index], ""]
            parts.append(f"<h2>{escape(titles[index])}</h2><p class='requirement'>{escape(requirements[index])}</p>")
            for text in sections[index]:
                document.add_paragraph(text)
                markdown += [text, ""]
                parts.append(f"<p>{escape(text)}</p>")
        html_pages.append("<section>" + "\n".join(parts) + "</section>")
    output = ROOT / "submission"
    output.mkdir(exist_ok=True)
    document.save(output / "report-review.docx")
    (output / "REPORT_REVIEW.md").write_text("\n".join(markdown), encoding="utf-8")
    html = """<!doctype html><html lang='en'><meta charset='utf-8'><title>Food Rescue report review</title><style>
@page{size:A4;margin:14mm 16mm}body{font:9pt/1.17 Arial,sans-serif;color:#161e27;margin:0}h1{font-size:20pt;color:#172f56;margin:0 0 7pt}h2{font-size:12pt;color:#172f56;margin:10pt 0 5pt}p{margin:0 0 5pt}section{break-after:page}section:last-child{break-after:auto}.requirement{font-size:7.6pt;color:#666}.review{color:#9c331d;font-weight:bold}a{color:#17335c}</style>""" + "\n".join(html_pages) + "</html>"
    (output / "report-review.html").write_text(html, encoding="utf-8")
    print("Created local review DOCX, HTML and Markdown in submission/. Human confirmation and final links remain pending.")


if __name__ == "__main__":
    main()
