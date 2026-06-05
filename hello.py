"""
hello.py — SMS Platform CLI Entry Point & Quick-Start Launcher

Provides a colourful command-line interface to:
  - Launch the full platform (uvicorn + frontend)
  - Run the health check against a live server
  - Seed demo data for Chandler Bing
  - Print system information and Python environment details
  - Display the daily Chandler Bing quote

Usage:
    python hello.py
    python hello.py --check
    python hello.py --seed
    python hello.py --info
"""
from __future__ import annotations

import argparse
import os
import platform
import subprocess
import sys
from datetime import datetime

# Configure stdout to use UTF-8 (fixes UnicodeEncodeError on Windows terminals)
try:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

# ─── ANSI colours ─────────────────────────────────────────────────────────────
PURPLE = "\033[95m"
CYAN   = "\033[96m"
GREEN  = "\033[92m"
YELLOW = "\033[93m"
RED    = "\033[91m"
BOLD   = "\033[1m"
RESET  = "\033[0m"

BANNER = f"""
{PURPLE}{BOLD}╔══════════════════════════════════════════════════════════╗
║      Student Management System  ·  SMS Platform v2.0     ║
║          AI-Powered · FastAPI · Python · SQLite           ║
╚══════════════════════════════════════════════════════════╝{RESET}
{CYAN}  Student : Chandler Bing{RESET}
{CYAN}  Started : {datetime.now().strftime("%Y-%m-%d  %H:%M:%S")}{RESET}
"""

SMS_QUOTE = (
    "Could this SMS platform BE any more feature-complete?"
)


def print_banner() -> None:
    print(BANNER)
    print(f"  {YELLOW} {SMS_QUOTE}{RESET}\n")


def print_info() -> None:
    """Print Python and system environment information."""
    print(f"\n{BOLD}{CYAN}System Information{RESET}")
    print("─" * 50)
    print(f"  Python      : {sys.version.split()[0]}")
    print(f"  Platform    : {platform.system()} {platform.release()}")
    print(f"  Architecture: {platform.machine()}")
    print(f"  Executable  : {sys.executable}")
    print(f"  CWD         : {os.getcwd()}")
    print("─" * 50)

    # Check key packages
    packages = ["fastapi", "uvicorn", "sqlalchemy", "sklearn", "numpy", "pydantic"]
    print(f"\n{BOLD}Installed Packages{RESET}")
    print("─" * 50)
    for pkg in packages:
        try:
            import importlib
            mod = importlib.import_module(pkg)
            version = getattr(mod, "__version__", "?")
            print(f"  {GREEN}✓{RESET}  {pkg:<15} {CYAN}{version}{RESET}")
        except Exception:
            print(f"  {RED}✗{RESET}  {pkg:<15} {RED}not installed{RESET}")
    print("─" * 50 + "\n")


def run_server() -> None:
    """Launch the uvicorn server (same as run.py)."""
    print(f"\n{GREEN}Launching SMS server …{RESET}\n")
    backend_dir = os.path.join(os.path.dirname(__file__), "backend")
    subprocess.run(
        [sys.executable, "-m", "uvicorn", "app.main:app", "--reload", "--host", "127.0.0.1", "--port", "8000"],
        cwd=backend_dir,
    )


def run_health_check() -> None:
    """Run the health check script."""
    script = os.path.join(os.path.dirname(__file__), "scripts", "check_health.py")
    if os.path.exists(script):
        subprocess.run([sys.executable, script])
    else:
        print(f"{RED}Health check script not found at {script}{RESET}")


def seed_data(reset: bool = False) -> None:
    """Run the demo data seeder."""
    script = os.path.join(os.path.dirname(__file__), "scripts", "seed_demo_data.py")
    if os.path.exists(script):
        cmd = [sys.executable, script]
        if reset:
            cmd.append("--reset")
        subprocess.run(cmd)
    else:
        print(f"{RED}Seed script not found at {script}{RESET}")


def print_available_commands() -> None:
    print(f"{BOLD}Available Commands:{RESET}")
    print("─" * 55)
    cmds = [
        ("python hello.py",           "Launch the SMS platform server"),
        ("python hello.py --check",   "Run API endpoint health checks"),
        ("python hello.py --seed",    "Seed database with Chandler Bing demo data"),
        ("python hello.py --reset",   "Wipe & re-seed database (destructive)"),
        ("python hello.py --info",    "Show Python environment info"),
        ("python run.py",             "Alternative server launcher"),
    ]
    for cmd, desc in cmds:
        print(f"  {CYAN}{cmd:<38}{RESET} {desc}")
    print("─" * 55 + "\n")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="SMS Platform — Chandler Bing's Student Management System",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("--check",  action="store_true", help="Run API health check")
    parser.add_argument("--seed",   action="store_true", help="Seed demo data")
    parser.add_argument("--reset",  action="store_true", help="Wipe & re-seed database")
    parser.add_argument("--info",   action="store_true", help="Show environment info")
    args = parser.parse_args()

    print_banner()

    if args.info:
        print_info()
        return

    if args.check:
        run_health_check()
        return

    if args.reset:
        seed_data(reset=True)
        return

    if args.seed:
        seed_data(reset=False)
        return

    # Default: show info and start server
    print_info()
    print_available_commands()
    run_server()


if __name__ == "__main__":
    main()
