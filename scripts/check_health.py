"""
scripts/check_health.py — SMS Platform Health Check Script

Verifies the server is running and all key API endpoints are responsive.
Prints a colour-coded report of endpoint statuses.

Usage:
    python scripts/check_health.py
    python scripts/check_health.py --host 127.0.0.1 --port 8000
"""
from __future__ import annotations

import argparse
import sys
import time
from typing import NamedTuple

try:
    import urllib.request
    import urllib.error
    import json as _json
except ImportError:
    pass  # stdlib — always available


# ─── ANSI colours ────────────────────────────────────────────────────────────
GREEN  = "\033[92m"
YELLOW = "\033[93m"
RED    = "\033[91m"
CYAN   = "\033[96m"
BOLD   = "\033[1m"
RESET  = "\033[0m"


class EndpointResult(NamedTuple):
    path: str
    status_code: int
    latency_ms: float
    ok: bool
    snippet: str


ENDPOINTS_TO_CHECK = [
    "/api/health",
    "/api/courses",
    "/api/tasks",
    "/api/routine",
    "/api/skills/targets",
    "/api/analytics/gpa",
    "/api/analytics/burnout",
    "/api/notifications/alerts",
    "/api/notifications/quote",
    "/api/report/weekly",
    "/api/streak",
    "/api/student/profile",
]


def check_endpoint(base_url: str, path: str, timeout: int = 5) -> EndpointResult:
    url = f"{base_url}{path}"
    t0 = time.perf_counter()
    try:
        with urllib.request.urlopen(url, timeout=timeout) as resp:  # noqa: S310
            latency_ms = (time.perf_counter() - t0) * 1000
            raw = resp.read().decode("utf-8")
            try:
                data = _json.loads(raw)
                snippet = str(data)[:80]
            except ValueError:
                snippet = raw[:80]
            return EndpointResult(
                path=path,
                status_code=resp.status,
                latency_ms=round(latency_ms, 1),
                ok=True,
                snippet=snippet,
            )
    except urllib.error.HTTPError as exc:
        latency_ms = (time.perf_counter() - t0) * 1000
        return EndpointResult(path=path, status_code=exc.code, latency_ms=round(latency_ms, 1), ok=False, snippet=str(exc))
    except Exception as exc:
        return EndpointResult(path=path, status_code=0, latency_ms=0.0, ok=False, snippet=str(exc))


def print_result(result: EndpointResult) -> None:
    icon   = f"{GREEN}✓{RESET}" if result.ok else f"{RED}✗{RESET}"
    code   = f"{GREEN}{result.status_code}{RESET}" if result.ok else f"{RED}{result.status_code}{RESET}"
    lat    = f"{CYAN}{result.latency_ms:.1f}ms{RESET}"
    path   = f"{BOLD}{result.path:<40}{RESET}"
    print(f"  {icon}  {path}  {code}  {lat}")
    if not result.ok:
        print(f"       {YELLOW}↳ {result.snippet[:100]}{RESET}")


def run(host: str, port: int) -> int:
    base_url = f"http://{host}:{port}"
    print(f"\n{BOLD}{CYAN}SMS Platform Health Check{RESET}")
    print(f"  Target : {base_url}")
    print(f"  Probing {len(ENDPOINTS_TO_CHECK)} endpoint(s) …\n")
    print("─" * 65)

    results = [check_endpoint(base_url, ep) for ep in ENDPOINTS_TO_CHECK]

    print("─" * 65)
    for r in results:
        print_result(r)
    print("─" * 65)

    passed = sum(1 for r in results if r.ok)
    failed = len(results) - passed
    avg_lat = sum(r.latency_ms for r in results if r.ok) / max(passed, 1)

    print(f"\n  {GREEN}Passed: {passed}{RESET}  {RED}Failed: {failed}{RESET}  Avg latency: {CYAN}{avg_lat:.1f}ms{RESET}\n")
    return 0 if failed == 0 else 1


def main() -> None:
    parser = argparse.ArgumentParser(description="Check SMS API endpoint health.")
    parser.add_argument("--host", default="127.0.0.1", help="Server host")
    parser.add_argument("--port", type=int, default=8000, help="Server port")
    args = parser.parse_args()
    sys.exit(run(args.host, args.port))


if __name__ == "__main__":
    main()
