"""Reproduce each reported bug and save a screenshot as evidence (docs/evidence/).

    python scripts/capture_evidence.py
"""
import functools
import http.server
import socketserver
import threading
from pathlib import Path

from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "docs" / "evidence"


def highlight(page, test_ids):
    page.evaluate("""ids => ids.forEach(id => document.querySelectorAll(`[data-testid="${id}"]`)
        .forEach(el => { el.style.outline = '3px solid #D32F2F'; el.style.outlineOffset = '3px'; }))""", test_ids)


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    class Quiet(http.server.SimpleHTTPRequestHandler):
        def log_message(self, *args):
            pass

    handler = functools.partial(Quiet, directory=str(ROOT / "app"))
    with socketserver.TCPServer(("127.0.0.1", 0), handler) as server:
        threading.Thread(target=server.serve_forever, daemon=True).start()
        url = f"http://127.0.0.1:{server.server_address[1]}/index.html"
        with sync_playwright() as p:
            browser = p.chromium.launch()

            def fresh(width=1280, height=820):
                page = browser.new_page(viewport={"width": width, "height": height}, device_scale_factor=2)
                page.goto(url)
                return page

            add = lambda page, name: page.get_by_role("button", name=f"Adicionar {name}").click()  # noqa: E731

            # BUG-001: price sort
            page = fresh()
            page.get_by_test_id("sort").select_option("price-asc")
            highlight(page, ["product-price"])
            page.get_by_test_id("product-list").screenshot(path=OUT / "BUG-001-price-sort.png")
            page.close()

            # BUG-002: coupon stacks
            page = fresh()
            add(page, "Bolo de rolo (fatia)"); add(page, "Bolo de rolo (fatia)")
            for _ in range(3):
                page.get_by_test_id("coupon-input").fill("BOAVIAGEM10")
                page.get_by_test_id("coupon-apply").click()
            highlight(page, ["discount", "total"])
            page.locator("#cart").screenshot(path=OUT / "BUG-002-coupon-stacks.png")
            page.close()

            # BUG-003: phone with letters accepted
            page = fresh()
            add(page, "Café coado")
            page.get_by_test_id("checkout-button").click()
            page.get_by_test_id("name-input").fill("Ana Souza")
            page.get_by_test_id("phone-input").fill("abcdefghijk")
            page.get_by_test_id("pickup-input").fill("08:30")
            page.get_by_test_id("place-order").click()
            highlight(page, ["order-number"])
            page.get_by_test_id("confirmation").screenshot(path=OUT / "BUG-003-phone-letters-accepted.png")
            page.close()

            # BUG-004: totals not updated after removing an item
            page = fresh()
            add(page, "Café coado"); add(page, "Cappuccino")
            page.get_by_role("button", name="Remover Cappuccino").click()
            highlight(page, ["subtotal", "total", "cart-items"])
            page.locator("#cart").screenshot(path=OUT / "BUG-004-stale-total.png")
            page.close()
            browser.close()
        server.shutdown()
    print("Evidence saved to", OUT)


if __name__ == "__main__":
    main()
