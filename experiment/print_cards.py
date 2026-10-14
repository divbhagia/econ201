"""Print the card sheets and the run sheet in experiment/ to PDF with Chromium.

Run from the course root with the Python that has Playwright:

    ~/.pyenv/versions/3.12.1/bin/python experiment/print_cards.py

The cards are print-only and never published, so they are not tagged.
"""

from pathlib import Path

from playwright.sync_api import sync_playwright

HERE = Path(__file__).resolve().parent

with sync_playwright() as p:
    browser = p.chromium.launch()
    page = browser.new_page()
    for name in ("cards-buyers", "cards-sellers", "run-sheet"):
        if not (HERE / f"{name}.html").exists():
            continue
        page.goto((HERE / f"{name}.html").as_uri())
        page.wait_for_timeout(300)
        page.pdf(path=str(HERE / f"{name}.pdf"), format="Letter", print_background=True,
                 prefer_css_page_size=True)
        print(f"wrote experiment/{name}.pdf")
    browser.close()
