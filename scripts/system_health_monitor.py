# -*- coding: utf-8 -*-
#!/usr/bin/env python3
"""
=============================================================
  AccuKnox QA Trainee Assignment — Problem Statement 1
  System Health Monitoring Script
  Author : Irshad Ansari
  Language: Python 3
=============================================================
Monitors CPU, Memory, Disk, and Running Processes.
Logs alerts to console AND a log file when thresholds are exceeded.

Usage:
    python3 system_health_monitor.py              # single run
    python3 system_health_monitor.py --watch 60   # repeat every 60 seconds
"""

import argparse
import logging
import os
import time
from datetime import datetime

try:
    import psutil
except ImportError:
    print("[ERROR] 'psutil' is required. Install it with: pip install psutil")
    raise SystemExit(1)

# ── Configuration / Thresholds ────────────────────────────────────────────────
THRESHOLDS = {
    "cpu_percent":    80.0,   # %
    "memory_percent": 80.0,   # %
    "disk_percent":   85.0,   # %
    "top_process_n":  5,      # show top N processes by CPU
}

LOG_FILE = "system_health.log"

# ── Logging Setup ─────────────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)-8s  %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler(LOG_FILE, encoding="utf-8"),
    ],
)
logger = logging.getLogger("HealthMonitor")

# ── ANSI Colors (console only) ────────────────────────────────────────────────
GREEN  = "\033[92m"
YELLOW = "\033[93m"
RED    = "\033[91m"
CYAN   = "\033[96m"
BOLD   = "\033[1m"
RESET  = "\033[0m"

def color(text, code):
    return f"{code}{text}{RESET}"

def status_label(value, threshold):
    if value >= threshold:
        return color("ALERT", RED + BOLD), True
    if value >= threshold * 0.85:
        return color("WARN ", YELLOW), False
    return color("OK   ", GREEN), False

# ── Metric Collectors ─────────────────────────────────────────────────────────
def check_cpu():
    cpu = psutil.cpu_percent(interval=1)
    count = psutil.cpu_count(logical=True)
    label, alert = status_label(cpu, THRESHOLDS["cpu_percent"])
    return {
        "metric": "CPU Usage",
        "value": cpu,
        "unit": "%",
        "threshold": THRESHOLDS["cpu_percent"],
        "cores": count,
        "label": label,
        "alert": alert,
    }

def check_memory():
    mem = psutil.virtual_memory()
    label, alert = status_label(mem.percent, THRESHOLDS["memory_percent"])
    return {
        "metric": "Memory Usage",
        "value": mem.percent,
        "unit": "%",
        "threshold": THRESHOLDS["memory_percent"],
        "used_gb": mem.used / 1e9,
        "total_gb": mem.total / 1e9,
        "available_gb": mem.available / 1e9,
        "label": label,
        "alert": alert,
    }

def check_disk():
    results = []
    for part in psutil.disk_partitions(all=False):
        try:
            usage = psutil.disk_usage(part.mountpoint)
        except PermissionError:
            continue
        label, alert = status_label(usage.percent, THRESHOLDS["disk_percent"])
        results.append({
            "metric": f"Disk  [{part.mountpoint}]",
            "value": usage.percent,
            "unit": "%",
            "threshold": THRESHOLDS["disk_percent"],
            "used_gb": usage.used / 1e9,
            "total_gb": usage.total / 1e9,
            "free_gb": usage.free / 1e9,
            "label": label,
            "alert": alert,
        })
    return results

def check_processes():
    procs = []
    for p in psutil.process_iter(["pid", "name", "cpu_percent", "memory_percent", "status"]):
        try:
            procs.append(p.info)
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue
    # sort by CPU desc
    procs.sort(key=lambda x: x.get("cpu_percent") or 0, reverse=True)
    return procs[: THRESHOLDS["top_process_n"]]

# ── Report Printer ────────────────────────────────────────────────────────────
def print_separator(char="─", width=62):
    print(color(char * width, CYAN))

def print_header():
    now = datetime.now().strftime("%Y-%m-%d  %H:%M:%S")
    print_separator("═")
    print(color(f"  🖥️  SYSTEM HEALTH MONITOR    {now}", BOLD + CYAN))
    print_separator("═")

def print_metric_row(m):
    bar_len = 30
    filled = int((m["value"] / 100) * bar_len)
    bar_char = color("█" * filled, RED if m["alert"] else GREEN)
    bar = bar_char + color("░" * (bar_len - filled), "\033[90m")
    line = (
        f"  {m['label']}  {m['metric']:<28}"
        f"  {m['value']:5.1f}{m['unit']}  [{bar}]"
        f"  (threshold: {m['threshold']}%)"
    )
    print(line)
    if m["alert"]:
        logger.warning(
            "ALERT -- %s is %.1f%% (threshold: %.1f%%)",
            m["metric"].strip(), m["value"], m["threshold"]
        )

def print_processes(procs):
    print_separator()
    print(color(f"  {'PID':<8}{'NAME':<28}{'CPU%':>7}{'MEM%':>7}  STATUS", BOLD))
    print_separator()
    for p in procs:
        cpu = p.get("cpu_percent") or 0
        mem = p.get("memory_percent") or 0
        cpu_str = color(f"{cpu:>6.1f}%", RED if cpu > 50 else RESET)
        print(f"  {p['pid']:<8}{(p['name'] or '?'):<28}{cpu_str}{mem:>6.1f}%  {p.get('status','')}")

# ── Main Run ──────────────────────────────────────────────────────────────────
def run_check():
    print_header()
    alerts = 0

    # CPU
    cpu = check_cpu()
    print_separator()
    print(color(f"  CPU  ({cpu['cores']} logical cores)", BOLD))
    print_separator()
    print_metric_row(cpu)
    if cpu["alert"]:
        alerts += 1

    # Memory
    mem = check_memory()
    print_separator()
    print(color("  MEMORY", BOLD))
    print_separator()
    print_metric_row(mem)
    print(
        f"    Used: {mem['used_gb']:.2f} GB  |  "
        f"Available: {mem['available_gb']:.2f} GB  |  "
        f"Total: {mem['total_gb']:.2f} GB"
    )
    if mem["alert"]:
        alerts += 1

    # Disk
    disks = check_disk()
    print_separator()
    print(color("  DISK", BOLD))
    print_separator()
    for d in disks:
        print_metric_row(d)
        print(
            f"    Used: {d['used_gb']:.2f} GB  |  "
            f"Free: {d['free_gb']:.2f} GB  |  "
            f"Total: {d['total_gb']:.2f} GB"
        )
        if d["alert"]:
            alerts += 1

    # Processes
    procs = check_processes()
    print_separator()
    print(color(f"  TOP {THRESHOLDS['top_process_n']} PROCESSES BY CPU", BOLD))
    print_processes(procs)

    # Summary
    print_separator("═")
    if alerts:
        summary = color(f"  ⚠️  {alerts} ALERT(S) DETECTED — check {LOG_FILE} for details", RED + BOLD)
    else:
        summary = color("  ✅  All systems healthy — no thresholds exceeded", GREEN + BOLD)
    print(summary)
    print_separator("═")
    logger.info("Health check complete. Alerts triggered: %d", alerts)
    return alerts

def main():
    parser = argparse.ArgumentParser(description="System Health Monitor")
    parser.add_argument(
        "--watch", type=int, metavar="SECONDS",
        help="Repeat check every N seconds (omit for single run)"
    )
    args = parser.parse_args()

    if args.watch:
        print(color(f"\n  Watching system every {args.watch}s — press Ctrl+C to stop\n", CYAN))
        try:
            while True:
                run_check()
                time.sleep(args.watch)
        except KeyboardInterrupt:
            print(color("\n  Monitoring stopped.", YELLOW))
    else:
        run_check()

if __name__ == "__main__":
    main()
