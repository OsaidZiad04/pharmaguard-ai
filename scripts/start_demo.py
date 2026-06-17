from __future__ import annotations

import argparse
import os
from pathlib import Path
import shutil
import subprocess
import sys
import time
import webbrowser


REPO_ROOT = Path(__file__).resolve().parents[1]
BACKEND_DIR = REPO_ROOT / "backend"
FRONTEND_DIR = REPO_ROOT / "frontend"


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Check or launch the local PharmaGuard AI demo."
    )
    parser.add_argument(
        "--launch",
        action="store_true",
        help="Launch backend and frontend in the current terminal session context.",
    )
    args = parser.parse_args()

    print("PharmaGuard AI local demo checker")
    print("Prototype only. Not clinical validation. Pharmacist review required.")
    print("")

    checks = run_checks()
    failures = [check for check in checks if check[0] == "FAIL"]

    for status, message in checks:
        print(f"{status}: {message}")

    print("")
    if failures:
        print("Resolve FAIL items before launching the demo.")
        return 1

    if args.launch:
        return launch_demo()

    print("Next steps:")
    print("- Windows one-click: start-pharmaguard-demo.bat")
    print("- Manual backend: cd backend && python -m uvicorn app.main:app --reload")
    print("- Manual frontend: cd frontend && npm.cmd run dev")
    print("- Open: http://localhost:3000")
    print("- Evidence: http://localhost:3000/evaluation")
    return 0


def run_checks() -> list[tuple[str, str]]:
    checks: list[tuple[str, str]] = []

    if sys.version_info >= (3, 11):
        checks.append(("PASS", f"Python version {sys.version.split()[0]} detected."))
    else:
        checks.append(("FAIL", "Python 3.11+ is recommended for the backend."))

    checks.append(_exists(BACKEND_DIR, "backend directory exists"))
    checks.append(_exists(FRONTEND_DIR, "frontend directory exists"))
    checks.append(_exists(BACKEND_DIR / "requirements.txt", "backend requirements file exists"))
    checks.append(_exists(FRONTEND_DIR / "package.json", "frontend package.json exists"))

    node = shutil.which("node")
    checks.append(("PASS", f"Node.js found: {node}") if node else ("FAIL", "Node.js not found."))

    npm = shutil.which("npm.cmd") or shutil.which("npm")
    checks.append(("PASS", f"npm found: {npm}") if npm else ("FAIL", "npm not found."))

    if (FRONTEND_DIR / "node_modules").exists():
        checks.append(("PASS", "frontend node_modules exists."))
    else:
        checks.append(("WARN", "frontend node_modules missing. Run 'cd frontend && npm.cmd install'."))

    try:
        import fastapi  # noqa: F401
        import uvicorn  # noqa: F401

        checks.append(("PASS", "FastAPI and uvicorn are importable in this Python environment."))
    except ImportError:
        checks.append(
            (
                "WARN",
                "FastAPI/uvicorn are not importable in this Python environment. Activate backend/.venv or install backend requirements.",
            )
        )

    checks.append(("PASS", "Tesseract is optional and not required for demo startup."))
    return checks


def launch_demo() -> int:
    python_exe = _preferred_python()
    npm_exe = shutil.which("npm.cmd") or shutil.which("npm")
    if not npm_exe:
        print("FAIL: npm not found.")
        return 1

    print("Launching backend and frontend. Press Ctrl+C in their terminals to stop.")
    backend = subprocess.Popen(
        [python_exe, "-m", "uvicorn", "app.main:app", "--reload", "--host", "127.0.0.1", "--port", "8000"],
        cwd=BACKEND_DIR,
    )
    frontend = subprocess.Popen(
        [npm_exe, "run", "dev", "--", "--hostname", "127.0.0.1", "--port", "3000"],
        cwd=FRONTEND_DIR,
    )
    print(f"backend pid: {backend.pid}")
    print(f"frontend pid: {frontend.pid}")
    print("Opening http://localhost:3000")
    time.sleep(5)
    webbrowser.open("http://localhost:3000")
    print("This helper does not manage long-term process shutdown. Use Ctrl+C or the stop scripts.")
    return 0


def _preferred_python() -> str:
    candidates = [
        BACKEND_DIR / ".venv" / "Scripts" / "python.exe",
        REPO_ROOT / ".venv" / "Scripts" / "python.exe",
    ]
    for candidate in candidates:
        if candidate.exists():
            return str(candidate)
    return sys.executable


def _exists(path: Path, message: str) -> tuple[str, str]:
    return ("PASS", message) if path.exists() else ("FAIL", f"Missing {path}")


if __name__ == "__main__":
    raise SystemExit(main())
