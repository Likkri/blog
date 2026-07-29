from __future__ import annotations

import threading
import unittest
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

from site_health_check import check_once, check_with_retries


class _Handler(BaseHTTPRequestHandler):
    attempts = 0

    def do_GET(self) -> None:
        type(self).attempts += 1
        if self.path == "/ok":
            self.send_response(200)
            body = "覃科宁的博客".encode()
        elif self.path == "/missing":
            self.send_response(200)
            body = b"different content"
        elif self.path == "/transient" and type(self).attempts < 3:
            self.send_response(503)
            body = b"retry"
        elif self.path == "/not-found":
            self.send_response(404)
            body = b"not found"
        else:
            self.send_response(200)
            body = b"recovered"

        self.send_header("Content-Type", "text/plain; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, _format: str, *_args: object) -> None:
        return


class SiteHealthCheckTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.server = ThreadingHTTPServer(("127.0.0.1", 0), _Handler)
        cls.thread = threading.Thread(target=cls.server.serve_forever, daemon=True)
        cls.thread.start()
        cls.base_url = f"http://127.0.0.1:{cls.server.server_port}"

    @classmethod
    def tearDownClass(cls) -> None:
        cls.server.shutdown()
        cls.thread.join(timeout=2)
        cls.server.server_close()

    def setUp(self) -> None:
        _Handler.attempts = 0

    def test_success_with_content_check(self) -> None:
        result = check_once(
            f"{self.base_url}/ok",
            contains="覃科宁的博客",
        )
        self.assertTrue(result.ok)
        self.assertEqual(result.status, 200)
        self.assertTrue(result.content_matched)

    def test_missing_content_is_unhealthy(self) -> None:
        result = check_once(
            f"{self.base_url}/missing",
            contains="expected",
        )
        self.assertFalse(result.ok)
        self.assertEqual(result.status, 200)
        self.assertFalse(result.content_matched)

    def test_retries_transient_server_errors(self) -> None:
        result = check_with_retries(
            f"{self.base_url}/transient",
            retries=2,
            backoff=0,
        )
        self.assertTrue(result.ok)
        self.assertEqual(result.attempt, 3)
        self.assertEqual(_Handler.attempts, 3)

    def test_does_not_retry_client_error(self) -> None:
        result = check_with_retries(
            f"{self.base_url}/not-found",
            retries=3,
            backoff=0,
        )
        self.assertFalse(result.ok)
        self.assertEqual(result.status, 404)
        self.assertEqual(_Handler.attempts, 1)

    def test_rejects_relative_url(self) -> None:
        with self.assertRaisesRegex(ValueError, "absolute"):
            check_once("/relative")


if __name__ == "__main__":
    unittest.main()
