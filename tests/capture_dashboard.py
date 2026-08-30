from playwright.sync_api import sync_playwright
from pathlib import Path
import time

# ============================================================
# REVIVEAI DASHBOARD SCREENSHOT AUTOMATION
# ============================================================

BASE_URL = "http://localhost:8502"
OUTPUT_DIR = Path("docs")

OUTPUT_DIR.mkdir(exist_ok=True)


def save_screenshot(page, filename):
    path = OUTPUT_DIR / filename
    page.screenshot(
        path=str(path),
        full_page=True
    )
    print(f"Saved: {path}")


with sync_playwright() as p:

    browser = p.chromium.launch(headless=True)

    page = browser.new_page(
        viewport={
            "width": 1600,
            "height": 1000
        }
    )

    print("=" * 70)
    print("REVIVEAI DASHBOARD SCREENSHOT AUTOMATION")
    print("=" * 70)

    # --------------------------------------------------------
    # OPEN DASHBOARD
    # --------------------------------------------------------

    print("\nOpening ReviveAI dashboard...")

    page.goto(
        BASE_URL,
        wait_until="networkidle"
    )

    time.sleep(3)

    # --------------------------------------------------------
    # RECOVERY OVERVIEW
    # --------------------------------------------------------

    print("\nCapturing Recovery Overview...")

    save_screenshot(
        page,
        "dashboard_overview.png"
    )

    # --------------------------------------------------------
    # AGENT INTELLIGENCE
    # --------------------------------------------------------

    print("\nOpening Agent Intelligence...")

    agent_tab = page.get_by_text(
        "Agent Intelligence",
        exact=False
    ).first

    agent_tab.click()

    time.sleep(2)

    save_screenshot(
        page,
        "agent_intelligence.png"
    )

    # --------------------------------------------------------
    # TRANSACTION EXPLORER
    # --------------------------------------------------------

    print("\nOpening Transaction Explorer...")

    explorer_tab = page.get_by_text(
        "Transaction Explorer",
        exact=False
    ).first

    explorer_tab.click()

    time.sleep(2)

    # Find transaction input
    inputs = page.locator("input")

    if inputs.count() > 0:

        # Usually the first input is the Transaction ID field
        transaction_input = inputs.first

        transaction_input.fill("TXN103618")

        # Allow Streamlit to update
        time.sleep(3)

    save_screenshot(
        page,
        "transaction_explorer.png"
    )

    # --------------------------------------------------------
    # FINAL
    # --------------------------------------------------------

    browser.close()

    print("\n" + "=" * 70)
    print("SCREENSHOT CAPTURE COMPLETE")
    print("=" * 70)

    print("\nFiles created:")

    for file in OUTPUT_DIR.glob("*.png"):
        print(f"  ✓ {file}")
