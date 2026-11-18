"""Validate final handoff files and build the <=100 MB Moodle ZIP.

Requires a human-reviewed report.pdf and real webpage/video URLs; never silently
packages an incomplete handoff. Videos, environments and private notes are excluded.
"""
import argparse
import json
import sys
import zipfile
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parents[1]


def validate_links(links):
    errors = []
    for key in ("repository", "public_webpage", "presentation_youtube", "demo_youtube"):
        parsed = urlparse(links.get(key, ""))
        if parsed.scheme != "https" or not parsed.netloc:
            errors.append(f"Set a real HTTPS URL for {key} in submission/links.json")
        if "youtube" in key and parsed.hostname not in ("www.youtube.com", "youtube.com", "youtu.be"):
            errors.append(f"{key} must be a YouTube link")
    if links.get("presentation_youtube") == links.get("demo_youtube"):
        errors.append("The presentation and demo must have separate YouTube links")
    return errors


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="Validate without writing a ZIP")
    args = parser.parse_args()
    links = json.loads((ROOT / "submission/links.json").read_text(encoding="utf-8"))
    errors = validate_links(links)
    report = ROOT / "submission/report.pdf"
    review_path = ROOT / "submission/member_review.json"
    expected = json.loads((ROOT / "submission/member_review.example.json").read_text(encoding="utf-8"))
    if not review_path.is_file():
        errors.append("Complete the actual group review in submission/member_review.json")
    else:
        review = json.loads(review_path.read_text(encoding="utf-8"))
        for member in expected["member_signoff"]:
            if review.get("member_signoff", {}).get(member) is not True:
                errors.append(f"Member sign-off pending: {member}")
        for field in expected:
            if field != "member_signoff" and review.get(field) is not True:
                errors.append(f"Required group check pending: {field}")
    if not report.is_file():
        errors.append("Export and review the final report as submission/report.pdf")
    elif not report.read_bytes().startswith(b"%PDF-"):
        errors.append("submission/report.pdf must be an actual PDF")
    else:
        try:
            from pypdf import PdfReader
            text = "\n".join(page.extract_text() or "" for page in PdfReader(report).pages)
            if "REVIEW COPY" in text or "Pending team publication/recording" in text:
                errors.append("Remove review-copy notices and unresolved links from the final report")
        except ImportError:
            errors.append("Install requirements-dev.txt for the PDF readiness check")
    if errors:
        print("Submission is not ready:\n- " + "\n- ".join(errors), file=sys.stderr)
        return 1
    if args.check:
        print("Required files, real-link fields and recorded group checks are present. Humans must still verify actual access and PDF layout.")
        return 0
    folder = ROOT / "submission"
    archive = folder / "food-rescue-group-40.zip"
    include = [ROOT / "README.md", ROOT / "requirements.txt", ROOT / "requirements-lock.txt", ROOT / "requirements-dev.txt", ROOT / "run_local.py", ROOT / "benchmark.py", ROOT / "streamlit_app.py", ROOT / "mcp.json", ROOT / ".env.example", ROOT / "agent.py", ROOT / "engine.py", ROOT / "normalizer.py"]
    for directory in ("src", "tests", "scripts", "data", "evidence", "docs", "skills", ".streamlit"):
        include.extend(p for p in (ROOT / directory).rglob("*") if p.is_file() and "__pycache__" not in p.parts and p.name != "secrets.toml")
    include.extend(ROOT / "submission" / name for name in ("links.json", "member_review.example.json", "CHECKLIST.md", "VIDEO_SCRIPTS.md"))
    include.append(ROOT / ".pi/skills/food-rescue/SKILL.md")
    link_text = "\n".join(f"{key}: {value}" for key, value in links.items() if value) + "\n"
    with zipfile.ZipFile(archive, "w", zipfile.ZIP_DEFLATED) as output:
        output.write(report, "report.pdf")
        output.writestr("links.txt", link_text)
        for path in include:
            output.write(path, "source/" + path.relative_to(ROOT).as_posix())
    if archive.stat().st_size > 100_000_000:
        raise SystemExit("ZIP exceeds 100 MB; reduce artifacts before uploading")
    print(f"Created {archive} ({archive.stat().st_size / 1_000_000:.2f} MB). No videos, keys or environments included.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
