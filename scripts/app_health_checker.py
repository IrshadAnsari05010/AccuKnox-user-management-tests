# -*- coding: utf-8 -*-
#!/usr/bin/env python3
"""
=============================================================
  AccuKnox QA Trainee Assignment — Problem Statement 4
  Application Health Checker
  Author : Irshad Ansari
  Language: Python 3
=============================================================
Checks uptime and health of one or more applications via HTTP.
Determines UP / DEGRADED / DOWN status from HTTP status codes
and response time. Logs a detailed report to console + file.

Usage:
    python3 app_health_checker.py                   # check built-in targets
    python3 app_health_checker.py --watch 30        # repeat every 30 seconds
    python3 app_health_checker.py --url https://...  # check single custom URL
"""

import argparse
import json
import logging
import time
import urllib.request
import urllib.error
from datetime import datetime

# ── Target Applications ───────────────────────────────────────────────────────
# Add / remove URLs here to monitor different applications
DEFAULT_TARGETS = [
    {
        "name": "OrangeHRM Demo (AUT)",
        "url": "https://opensource-demo.orangehrmlive.com/web/index.php/auth/login",
        "expected_status": 200,
        "timeout_sec": 10,
        "keyword": "OrangeHRM",        # optional: text that must appear in response
    },
    {
        "name": "AccuKnox Website",
        "url": "https://www.accuknox.com",
        "expected_status": 200,
        "timeout_sec": 10,
        "keyword": None,
    },
    {
        "name": "GitHub (API health)",
        "url": "https://api.github.com",
        "expected_status": 200,
        "timeout_sec": 10,
        "keyword": None,
    },
    {
        "name": "Simulated Down App",
        "url": "https://thisdomaindoesnotexistatall12345.com",
        "expected_status": 200,
        "timeout_sec": 5,
        "keyword": None,
    },
]

# ── Thresholds ────────────────────────────────────────────────────────────────
RESPONSE_TIME_WARN_MS  = 2000   # yellow if slower than this
RESPONSE_TIME_ALERT_MS = 5000   # red if slower than this

LOG_FILE = "app_health.log"

# ── Logging ───────────────────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)-8s  %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler(LOG_FILE, encoding="utf-8"),
    ],
)
logger = logging.getLogger("AppHealthChecker")

# ── ANSI Colors ───────────────────────────────────────────────────────────────
GREEN  = "\033[92m"
YELLOW = "\033[93m"
RED    = "\033[91m"
CYAN   = "\033[96m"
BOLD   = "\033[1m"
GREY   = "\033[90m"
RESET  = "\033[0m"

def clr(text, code):
    return f"{code}{text}{RESET}"

# ── HTTP Check ────────────────────────────────────────────────────────────────
def check_app(target):
    """
    Perform an HTTP GET and return a result dict with:
    - status: UP | DEGRADED | DOWN
    - http_code: integer or None
    - response_ms: float
    - keyword_found: bool or None
    - error: string or None
    """
    result = {
        "name":         target["name"],
        "url":          target["url"],
        "expected":     target["expected_status"],
        "http_code":    None,
        "response_ms":  None,
        "keyword_found": None,
        "status":       "DOWN",
        "error":        None,
    }

    start = time.perf_counter()
    try:
        req = urllib.request.Request(
            target["url"],
            headers={"User-Agent": "AccuKnox-HealthChecker/1.0"},
        )
        with urllib.request.urlopen(req, timeout=target["timeout_sec"]) as resp:
            elapsed_ms = (time.perf_counter() - start) * 1000
            result["http_code"]   = resp.status
            result["response_ms"] = round(elapsed_ms, 1)

            # Keyword check
            if target.get("keyword"):
                body = resp.read(4096).decode("utf-8", errors="ignore")
                result["keyword_found"] = target["keyword"].lower() in body.lower()
            else:
                result["keyword_found"] = None

            # Determine status
            if resp.status == target["expected_status"]:
                if target.get("keyword") and not result["keyword_found"]:
                    result["status"] = "DEGRADED"
                    result["error"]  = f"Keyword '{target['keyword']}' not found in response"
                elif elapsed_ms > RESPONSE_TIME_ALERT_MS:
                    result["status"] = "DEGRADED"
                    result["error"]  = f"Slow response: {elapsed_ms:.0f} ms"
                else:
                    result["status"] = "UP"
            else:
                result["status"] = "DEGRADED"
                result["error"]  = f"Unexpected HTTP {resp.status} (expected {target['expected_status']})"

    except urllib.error.HTTPError as e:
        elapsed_ms = (time.perf_counter() - start) * 1000
        result["http_code"]   = e.code
        result["response_ms"] = round(elapsed_ms, 1)
        result["status"]      = "DEGRADED" if e.code < 500 else "DOWN"
        result["error"]       = f"HTTP Error {e.code}: {e.reason}"

    except urllib.error.URLError as e:
        result["response_ms"] = round((time.perf_counter() - start) * 1000, 1)
        result["error"]       = f"Connection failed: {e.reason}"
        result["status"]      = "DOWN"

    except TimeoutError:
        result["response_ms"] = target["timeout_sec"] * 1000
        result["error"]       = f"Timed out after {target['timeout_sec']}s"
        result["status"]      = "DOWN"

    except Exception as e:
        result["response_ms"] = round((time.perf_counter() - start) * 1000, 1)
        result["error"]       = str(e)
        result["status"]      = "DOWN"

    return result

# ── Formatting ────────────────────────────────────────────────────────────────
STATUS_ICONS = {"UP": "✅", "DEGRADED": "⚠️ ", "DOWN": "❌"}
STATUS_COLORS = {"UP": GREEN, "DEGRADED": YELLOW, "DOWN": RED}

def format_response_time(ms):
    if ms is None:
        return clr("N/A", GREY)
    if ms > RESPONSE_TIME_ALERT_MS:
        return clr(f"{ms:.0f} ms", RED)
    if ms > RESPONSE_TIME_WARN_MS:
        return clr(f"{ms:.0f} ms", YELLOW)
    return clr(f"{ms:.0f} ms", GREEN)

def print_separator(char="─", width=66):
    print(clr(char * width, CYAN))

def print_result(r):
    icon  = STATUS_ICONS[r["status"]]
    color = STATUS_COLORS[r["status"]]
    label = clr(f"[{r['status']:<8}]", color + BOLD)

    print_separator()
    print(f"  {icon}  {label}  {clr(r['name'], BOLD)}")
    print(f"     {'URL':<14}: {clr(r['url'], GREY)}")
    print(f"     {'HTTP Code':<14}: {r['http_code'] or 'N/A'}")
    print(f"     {'Response Time':<14}: {format_response_time(r['response_ms'])}")

    if r["keyword_found"] is not None:
        kw_str = clr("Found ✓", GREEN) if r["keyword_found"] else clr("Not Found ✗", RED)
        print(f"     {'Keyword Check':<14}: {kw_str}")

    if r["error"]:
        print(f"     {'Issue':<14}: {clr(r['error'], YELLOW)}")

    # Log appropriately
    if r["status"] == "UP":
        logger.info("UP       | %-30s | %s ms | HTTP %s",
                    r["name"], r["response_ms"], r["http_code"])
    elif r["status"] == "DEGRADED":
        logger.warning("DEGRADED | %-30s | %s ms | %s",
                       r["name"], r["response_ms"], r["error"])
    else:
        logger.error("DOWN     | %-30s | %s", r["name"], r["error"])

# ── Main Report ───────────────────────────────────────────────────────────────
def run_checks(targets):
    now = datetime.now().strftime("%Y-%m-%d  %H:%M:%S")
    print_separator("═")
    print(clr(f"  🔍  APPLICATION HEALTH CHECKER    {now}", BOLD + CYAN))
    print_separator("═")

    results = []
    for t in targets:
        r = check_app(t)
        print_result(r)
        results.append(r)

    # Summary
    up       = sum(1 for r in results if r["status"] == "UP")
    degraded = sum(1 for r in results if r["status"] == "DEGRADED")
    down     = sum(1 for r in results if r["status"] == "DOWN")
    total    = len(results)

    print_separator("═")
    print(clr("  SUMMARY", BOLD + CYAN))
    print_separator()
    print(f"  Total Checked : {total}")
    print(f"  {clr('UP', GREEN + BOLD)}            : {up}")
    print(f"  {clr('DEGRADED', YELLOW + BOLD)}      : {degraded}")
    print(f"  {clr('DOWN', RED + BOLD)}          : {down}")
    print_separator("═")

    if down > 0 or degraded > 0:
        print(clr(f"  ⚠️  ACTION REQUIRED — {down} DOWN, {degraded} DEGRADED. See {LOG_FILE}", RED + BOLD))
    else:
        print(clr(f"  ✅  All {total} applications are UP and healthy.", GREEN + BOLD))
    print_separator("═")

    logger.info("Check complete -- UP: %d | DEGRADED: %d | DOWN: %d", up, degraded, down)
    return results

# ── Entry Point ───────────────────────────────────────────────────────────────
def main():
    parser = argparse.ArgumentParser(description="Application Health Checker")
    parser.add_argument("--url", help="Check a single custom URL")
    parser.add_argument("--watch", type=int, metavar="SECONDS",
                        help="Repeat checks every N seconds")
    args = parser.parse_args()

    if args.url:
        targets = [{
            "name": "Custom URL",
            "url": args.url,
            "expected_status": 200,
            "timeout_sec": 10,
            "keyword": None,
        }]
    else:
        targets = DEFAULT_TARGETS

    if args.watch:
        print(clr(f"\n  Watching {len(targets)} app(s) every {args.watch}s — Ctrl+C to stop\n", CYAN))
        try:
            while True:
                run_checks(targets)
                time.sleep(args.watch)
        except KeyboardInterrupt:
            print(clr("\n  Monitoring stopped.", YELLOW))
    else:
        run_checks(targets)

if __name__ == "__main__":
    main()
