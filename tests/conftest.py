"""Shared fixtures: serve the app locally so the suite runs anywhere (laptop or CI)
with no external website involved."""
import functools
import http.server
import socketserver
import threading
from pathlib import Path

import pytest

from pages.shop_page import ShopPage

APP_DIR = Path(__file__).resolve().parents[1] / "app"


class _QuietHandler(http.server.SimpleHTTPRequestHandler):
    def log_message(self, *args):  # keep test output clean
        pass


@pytest.fixture(scope="session")
def base_url():
    handler = functools.partial(_QuietHandler, directory=str(APP_DIR))
    with socketserver.TCPServer(("127.0.0.1", 0), handler) as server:
        port = server.server_address[1]
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        yield f"http://127.0.0.1:{port}"
        server.shutdown()


@pytest.fixture
def shop(page) -> ShopPage:
    return ShopPage(page).open()
