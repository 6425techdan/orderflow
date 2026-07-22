"""Capture Grafana OrderFlow dashboard screenshot (real UI, not fabricated)."""
from __future__ import annotations

from pathlib import Path

from playwright.sync_api import sync_playwright

OUT = Path(__file__).resolve().parents[2] / "docs" / "screenshots" / "grafana-red-queue.png"
URL = (
    "http://127.0.0.1:3000/d/orderflow-red-queue/orderflow-red-queue-slo"
    "?orgId=1&from=now-1h&to=now&refresh=5s&kiosk"
)


def main() -> int:
    OUT.parent.mkdir(parents=True, exist_ok=True)
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page(viewport={"width": 1800, "height": 1400})
        page.goto(URL, wait_until="networkidle", timeout=90_000)
        # Wait for Prometheus panel queries / canvas paint
        page.wait_for_timeout(15_000)
        try:
            page.wait_for_selector("canvas", timeout=30_000)
        except Exception:
            pass
        page.screenshot(path=str(OUT), full_page=True)
        browser.close()
    size = OUT.stat().st_size if OUT.exists() else 0
    print(f"wrote {OUT} bytes={size}")
    return 0 if size > 20_000 else 1


if __name__ == "__main__":
    raise SystemExit(main())
