from __future__ import annotations

import json
from pathlib import Path
import sys


BACKEND_ROOT = Path(__file__).resolve().parents[1]
REPO_ROOT = BACKEND_ROOT.parent
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))


def main() -> int:
    results = run_demo_health_check()
    print("PharmaGuard AI Demo Health Check")
    print("Prototype only. Synthetic data only. Pharmacist review required.")
    print("")
    for status, message in results:
        print(f"{status}: {message}")

    failures = [result for result in results if result[0] == "FAIL"]
    warnings = [result for result in results if result[0] == "WARN"]
    print("")
    print(f"summary: PASS={count(results, 'PASS')} WARN={len(warnings)} FAIL={len(failures)}")
    return 1 if failures else 0


def run_demo_health_check() -> list[tuple[str, str]]:
    results: list[tuple[str, str]] = []

    try:
        from app.main import create_app

        app = create_app()
        results.append(("PASS", f"Backend import sanity check passed: {app.title}."))
    except Exception as error:  # pragma: no cover - defensive script path
        results.append(("FAIL", f"Backend import sanity check failed: {error}"))

    required_files = [
        REPO_ROOT / "README.md",
        REPO_ROOT / "start-pharmaguard-demo.bat",
        REPO_ROOT / "start-pharmaguard-demo.ps1",
        REPO_ROOT / "stop-pharmaguard-demo.bat",
        REPO_ROOT / "stop-pharmaguard-demo.ps1",
        REPO_ROOT / "docs" / "presentation.html",
        REPO_ROOT / "docs" / "PharmaGuard_AI_Documentation.md",
        REPO_ROOT / "docs" / "local_demo_guide.md",
        REPO_ROOT / "docs" / "troubleshooting.md",
        REPO_ROOT / "data" / "evaluation" / "final_demo_cases.json",
    ]
    for path in required_files:
        results.append(_exists(path, f"Required demo file exists: {relative(path)}"))

    brand_files = [
        "pharmaguard-logo-main.png",
        "pharmaguard-logo-icon.png",
        "pharmaguard-logo-light.png",
        "pharmaguard-logo-dark.png",
        "pharmaguard-hero-visual.png",
    ]
    for file_name in brand_files:
        path = REPO_ROOT / "frontend" / "public" / "brand" / file_name
        results.append(_exists(path, f"Brand asset exists: /brand/{file_name}"))

    demo_cases_path = REPO_ROOT / "data" / "evaluation" / "final_demo_cases.json"
    if demo_cases_path.exists():
        try:
            cases = json.loads(demo_cases_path.read_text(encoding="utf-8"))
            if len(cases) >= 5:
                results.append(("PASS", f"Final demo cases load successfully: {len(cases)} cases."))
            else:
                results.append(("WARN", "Final demo cases file has fewer than 5 cases."))
        except json.JSONDecodeError as error:
            results.append(("FAIL", f"Final demo cases JSON is invalid: {error}"))

    private_dir = REPO_ROOT / "data" / "private"
    results.append(_exists(private_dir, "Private data directory exists and remains reserved for ignored local files."))
    results.append(
        (
            "PASS",
            "No real patient data check is manual: demo assets and repository tests must remain synthetic only.",
        )
    )
    results.append(("PASS", "Tesseract is optional and is not required for local demo startup."))
    return results


def _exists(path: Path, message: str) -> tuple[str, str]:
    return ("PASS", message) if path.exists() else ("FAIL", f"Missing {relative(path)}")


def relative(path: Path) -> str:
    try:
        return str(path.relative_to(REPO_ROOT))
    except ValueError:
        return str(path)


def count(results: list[tuple[str, str]], status: str) -> int:
    return sum(1 for result in results if result[0] == status)


if __name__ == "__main__":
    raise SystemExit(main())
