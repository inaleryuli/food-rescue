# Group 40: final submission handoff

**Due Friday 20 November 2026, 23:59 Hong Kong time (UTC+8). One team Moodle entry; ZIP at most 100 MB.** The supplied final rubric/template are authoritative over older midterm advice. Finish uploads earlier on Friday; keep time for signed-out link checks.

## Wednesday: each member verifies a concrete part

| Member | Suggested remaining work, extending the existing contribution | Completion evidence |
| --- | --- | --- |
| HU, Chengli (Rodrigo) | Review shared validation/agent/MCP and scope changes; prepare the final code revision and repository access | Run CLI refusal + MCP self-test; inspect final diff and secrets exclusions; record final commit |
| YU, Wei | Verify source quantities, alias preservation, dataset provenance and remaining data-quality limits | Spot-check recipes against originals, run importer/normalizer tests, review `data/provenance.json` |
| SIDARTA, Owen | Independently rerun suite/evaluation from a fresh clone after the revision is pushed; record continuous demo | Save real terminal results, confirm recall denominator/failures, record input-to-output and boundary cases |
| LO, Si Ching (Regina) | Review browser presets/manual entry/downloads, publish/check app and project page, assemble accessible presentation | Test download and mobile layout, signed-out working public links, readable slides/screens and captions |

These are proposed next tasks, not claims that those people already completed them. Each member also checks the report and supplies their actual section contributions and AI-use/human-verification details. Do not assign work from this AI-assisted finishing session to absent teammates.

## Exact remaining assignments: 18–20 November

Complete the following division by Wednesday 18 November, then record and finalize together on Thursday 19 November:

- **Rodrigo / HU, Chengli:** configure the group's private `.env` with the three provider settings; run `scripts/check_ai.py --live` using the project environment. A `live_ai` result is required before claiming API success. Review/report Sections 2 (actual pipeline) and 5 (ethics and all seven AI-use fields), and coordinate all members' verification details. Check repository access. Be the designated Moodle uploader on Friday.
- **YU, Wei:** spot-check five imported/seed recipes against their original pages, including quantities and the cantaloupe parsing fix; check scallion/green onion and courgette/zucchini aliases and dataset provenance. Draft/review Sections 1 (background/final scope) and 7 (references). Give Owen any source-data limitations to include.
- **SIDARTA, Owen:** fresh-clone the pushed revision; install from the lock; run the full suite, MCP self-check, benchmark and evaluation. Review Sections 3 (actual results) and 4 (reproduction/failure cases). Record the separate continuous demo showing input-to-output, download, test results and refusal. Say whether a real API call or offline fallback is being shown. Upload the demo to YouTube.
- **Regina / LO, Si Ching:** check presets/manual input/use-soon/time controls/download on desktop and mobile; deploy the app and publish the project webpage using the hosting instructions. Coordinate server-side AI configuration with Rodrigo. Assemble the short Zoom presentation/slides, upload it to YouTube, compile Section 6 from all four members' actual entries, and handle report layout/PDF export.

**All four on Thursday:** speak in the separate Zoom presentation (at most three minutes, each speaker's name visible); review every report section and record each person's specific contribution or “none”; confirm AI-use disclosures, watch both final videos, and check the exported report (body at most five pages). Each member supplies their own contribution statement; Regina compiles it rather than inventing it. Use `VIDEO_SCRIPTS.md` for speaking order and timing.

**Thursday after uploads:** Regina enters issued webpage/app and presentation links into `submission/links.json`; Owen supplies the separate demo URL; Rodrigo rebuilds the page/report, commits/pushes final link/content updates and checks the packaged ZIP. Recheck live links after publication. The recorded review PDF is a draft until the group completes human checks and links.

**Friday 20 November:** all four approve the actual files and complete any outstanding individual weekly reports. Rodrigo uploads the final ZIP well before 23:59 UTC+8; Owen downloads the submitted ZIP and checks its PDF and links; Regina verifies public webpage/video access while signed out; Wei checks the final references and source links. Rodrigo saves the Moodle receipt for the group.

## Thursday: public links, report, recordings

1. Review local product together: `python run_local.py`; run a preset, manual entry, use-soon toggle/time change, shopping-list download, and refusal. Confirm the final scope in `docs/FINAL_AUDIT.md`.
2. Commit/push the final reviewed files. Verify that teaching staff can access the complete GitHub repository. Keep the final commit hash for report and demo consistency.
3. Publish `docs/index.html` through GitHub Pages (`main` / `/docs`) and preferably the app through Streamlit Community Cloud. Follow `docs/REPRODUCIBILITY.md`. Use the actual issued URLs; test while signed out. A public project page is explicitly graded separately from the local app.
4. Update `submission/links.json` with **public_webpage**, **presentation_youtube**, **demo_youtube**, and optional **live_app**. These are intentionally blank until real URLs exist. Rebuild the page and report after updating.
5. Make a **separate Zoom presentation of at most 3 minutes**. All four members speak; each speaker's name is visible; faces optional. Use `VIDEO_SCRIPTS.md` as a rehearsable outline. Keep below 2:55 for margin.
6. Make a **separate demo video, unrestricted length**. Show continuous real execution from input through processing to output, evaluation results and an actual failure/boundary/refusal. Do not present cached JSON, mocks, cuts or simulated AI as continuous live execution. Say clearly that the AI integration was tested with mocks unless a real call is recorded.
7. Upload the two videos to YouTube with separate staff-accessible links. Unlisted is sufficient only if staff can open it without requesting access. Test audio, captions/readability and links while signed out. Neither video file needs to be in the Moodle ZIP.
8. Finish the report from the local review copy or `REPORT_REVIEW.md`: keep the template's section titles/grey requirements, remove example/review text, retain all seven AI-use fields, and complete Section 6 for **every member in each of Sections 1-7**, plus webpage/video work. Use specific completed work or **none**. Record review/disagreement honestly. Names belong in Section 6; **do not include UIDs or emails**. Keep private contribution details off the public webpage.
9. Report references, disclosure and contributions count in the **five-page body limit**; appendices do not. Main results cannot be moved out of the body merely to evade the limit. Export as `submission/report.pdf` and read the actual PDF to check page count, layout, links and leftovers. Do not submit a review copy.

## Friday: the very last group step

Meet briefly with all four members to confirm the actual submitted version, report contributions, both videos and public links. Copy `member_review.example.json` to `member_review.json` and mark checks true only after completing them. This local check is a handoff aid, not an extra course requirement.

```powershell
python scripts/package_submission.py --check
python scripts/package_submission.py
```

The builder validates the presence of a PDF, distinct YouTube URLs, public/repository URLs and the completed local review checklist. It includes `report.pdf`, `links.txt`, and a compact source/evidence copy. It excludes videos, environments, Git history, API keys and private working notes. It cannot certify remote link permissions, video duration/speaker participation or the PDF's visual quality: check those as people.

One designated uploader submits `submission/food-rescue-group-40.zip` to Moodle before 23:59 UTC+8. A second member downloads/opens the uploaded ZIP and rechecks report and links. Save the Moodle receipt and tell the team it is submitted. **Each member separately completes any outstanding weekly project report through the course's individual weekly-report process; the ZIP does not replace it.** Do not invent or backdate weekly progress. The rubric awards weekly-report marks using course records.
