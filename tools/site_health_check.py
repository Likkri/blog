#!/usr/bin/env python3
"""Small, dependency-free HTTP health check for personal sites and CI."""

from __future__ import annotations

import argparse
import json
import sys
import time
from dataclasses import asdict, dataclass
from typing import Iterable, Optional, Sequence, Tuple
from urllib.error import HTTPError, URLError
from urllib.parse import urlsplit
from urllib.request import Request, urlopen


DEFAULT_USER_AGENT = "site-health-check/1.0 (+https://qinkening.me)"


@dataclass(frozen=True)
class CheckResult:
    ok: bool
    url: str
    final_url: Optional[str]
    status: Optional[int]
    latency_ms: int
    attempt: int
    content_matched: Optional[bool]
    error: Optional[str]


def _validate_url(url: str) -> None:
    parsed = urlsplit(url)
    if parsed.scheme not in {"http", "https"} or not parsed.netloc:
        raise ValueError("URL must be an absolute http:// or https:// URL")


def check_once(
    url: str,
    *,
    expected_statuses: Iterable[int] = (200,),
    contains: Optional[str] = None,
    timeout: float = 8.0,
    user_agent: str = DEFAULT_USER_AGENT,
    attempt: int = 1,
    max_bytes: int = 2_000_000,
) -> CheckResult:
    """Perform one HTTP GET and return a structured result."""
    _validate_url(url)
    expected = set(expected_statuses)
    request = Request(url, headers={"User-Agent": user_agent}, method="GET")
    started = time.perf_counter()

    try:
        with urlopen(request, timeout=timeout) as response:
            status = response.status
            final_url = response.geturl()
            body = response.read(max_bytes + 1)
    except HTTPError as exc:
        status = exc.code
        final_url = exc.geturl()
        body = exc.read(max_bytes + 1)
    except (URLError, TimeoutError, OSError) as exc:
        return CheckResult(
            ok=False,
            url=url,
            final_url=None,
            status=None,
            latency_ms=round((time.perf_counter() - started) * 1000),
            attempt=attempt,
            content_matched=None,
            error=str(exc),
        )

    latency_ms = round((time.perf_counter() - started) * 1000)
    if len(body) > max_bytes:
        return CheckResult(
            ok=False,
            url=url,
            final_url=final_url,
            status=status,
            latency_ms=latency_ms,
            attempt=attempt,
            content_matched=None,
            error=f"response exceeded {max_bytes} bytes",
        )

    content_matched: Optional[bool] = None
    if contains is not None:
        text = body.decode("utf-8", errors="replace")
        content_matched = contains in text

    status_ok = status in expected
    content_ok = content_matched is not False
    error = None
    if not status_ok:
        error = f"unexpected HTTP status {status}"
    elif not content_ok:
        error = f"response did not contain {contains!r}"

    return CheckResult(
        ok=status_ok and content_ok,
        url=url,
        final_url=final_url,
        status=status,
        latency_ms=latency_ms,
        attempt=attempt,
        content_matched=content_matched,
        error=error,
    )


def check_with_retries(
    url: str,
    *,
    expected_statuses: Iterable[int] = (200,),
    contains: Optional[str] = None,
    timeout: float = 8.0,
    retries: int = 2,
    backoff: float = 0.75,
    user_agent: str = DEFAULT_USER_AGENT,
) -> CheckResult:
    """Retry network failures and server-side 5xx responses."""
    if retries < 0:
        raise ValueError("retries must be zero or greater")
    if backoff < 0:
        raise ValueError("backoff must be zero or greater")

    last_result: Optional[CheckResult] = None
    for attempt in range(1, retries + 2):
        last_result = check_once(
            url,
            expected_statuses=expected_statuses,
            contains=contains,
            timeout=timeout,
            user_agent=user_agent,
            attempt=attempt,
        )
        if last_result.ok:
            return last_result

        retryable = last_result.status is None or last_result.status >= 500
        if not retryable or attempt > retries:
            return last_result
        time.sleep(backoff * attempt)

    assert last_result is not None
    return last_result


def _parse_args(argv: Optional[Sequence[str]] = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Check a website's HTTP status and optional response text."
    )
    parser.add_argument("url", help="absolute http:// or https:// URL")
    parser.add_argument(
        "--expect-status",
        action="append",
        type=int,
        dest="expected_statuses",
        help="acceptable status code; repeat for multiple values (default: 200)",
    )
    parser.add_argument("--contains", help="text that must appear in the response")
    parser.add_argument("--timeout", type=float, default=8.0)
    parser.add_argument("--retries", type=int, default=2)
    parser.add_argument("--backoff", type=float, default=0.75)
    parser.add_argument("--user-agent", default=DEFAULT_USER_AGENT)
    parser.add_argument("--json", action="store_true", dest="as_json")
    return parser.parse_args(argv)


def main(argv: Optional[Sequence[str]] = None) -> int:
    args = _parse_args(argv)
    expected: Tuple[int, ...] = tuple(args.expected_statuses or [200])

    try:
        result = check_with_retries(
            args.url,
            expected_statuses=expected,
            contains=args.contains,
            timeout=args.timeout,
            retries=args.retries,
            backoff=args.backoff,
            user_agent=args.user_agent,
        )
    except ValueError as exc:
        print(f"configuration error: {exc}", file=sys.stderr)
        return 2

    if args.as_json:
        print(json.dumps(asdict(result), ensure_ascii=False, sort_keys=True))
    else:
        marker = "OK" if result.ok else "FAIL"
        detail = (
            f"status={result.status} latency={result.latency_ms}ms "
            f"attempt={result.attempt} final_url={result.final_url or '-'}"
        )
        print(f"{marker} {detail}")
        if result.error:
            print(result.error, file=sys.stderr)

    return 0 if result.ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
