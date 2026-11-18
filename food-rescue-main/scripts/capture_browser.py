"""Optional real Edge smoke test/screenshots; start Streamlit before running."""
import json
from datetime import datetime, timezone
from pathlib import Path
from playwright.sync_api import sync_playwright, expect

ROOT = Path(__file__).resolve().parents[1]


def main():
    assets = ROOT / "docs/assets"
    assets.mkdir(parents=True, exist_ok=True)
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(channel="msedge", headless=True)
        page = browser.new_page(viewport={"width": 1440, "height": 1050})
        page.goto("http://localhost:8501", wait_until="networkidle")
        page.get_by_role("button", name="Mushroom dinner", exact=True).click()
        expect(page.get_by_role("button", name="Export shopping list")).to_have_count(3)
        page.get_by_text("Cooking instructions", exact=True).first.click()
        expect(page.get_by_role("link", name="Open original recipe").first).to_be_visible()
        with page.expect_download() as download:
            page.get_by_role("button", name="Export shopping list").first.click()
        text = Path(download.value.path()).read_text(encoding="utf-8")
        assert "Check quantities" in text
        page.screenshot(path=str(assets / "browser-results.png"), full_page=True)
        page.get_by_role("button", name="Clear all", exact=True).click()
        entry = page.get_by_role("textbox", name="Add one ingredient at a time")
        entry.fill("bleach")
        entry.press("Enter")
        expect(page.get_by_text("[SAFETY REFUSAL]", exact=False)).to_be_visible()
        page.screenshot(path=str(assets / "browser-refusal.png"), full_page=True)
        page.set_viewport_size({"width": 390, "height": 844})
        page.get_by_role("button", name="Honey chicken", exact=True).click()
        expect(page.get_by_role("button", name="Export shopping list")).to_have_count(3)
        page.screenshot(path=str(assets / "browser-mobile.png"), full_page=True)
        browser.close()
    result = {"generated_at_utc": datetime.now(timezone.utc).isoformat(), "browser": "Microsoft Edge headless",
              "checks": ["real preset-to-recipe workflow", "source link", "shopping-list download content", "visible hazard refusal", "390px mobile results"],
              "passed": True, "scope": "Local live Streamlit app; no live model request"}
    (ROOT / "evidence/browser-smoke.json").write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print("PASS: live browser workflow, download, refusal and mobile viewport")


if __name__ == "__main__":
    main()
