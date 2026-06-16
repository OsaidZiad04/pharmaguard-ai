from __future__ import annotations

import argparse
from dataclasses import dataclass
from pathlib import Path
import subprocess
import sys


BACKEND_ROOT = Path(__file__).resolve().parents[1]
REPO_ROOT = BACKEND_ROOT.parent
FRONTEND_ROOT = REPO_ROOT / "frontend"


@dataclass(frozen=True)
class QaCommand:
    label: str
    command: list[str]
    cwd: Path
    optional: bool = False


def build_qa_commands() -> list[QaCommand]:
    return [
        _backend("generate OCR fixtures", "scripts/generate_ocr_fixtures.py"),
        _backend("inspect OCR fixtures", "scripts/inspect_ocr_fixtures.py"),
        QaCommand("backend tests", [sys.executable, "-m", "pytest"], BACKEND_ROOT),
        _backend("RAG evaluation", "scripts/evaluate_rag.py"),
        _backend("retrieval strategy evaluation", "scripts/evaluate_retrieval_strategies.py"),
        _backend("KB report", "scripts/kb_report.py"),
        _backend("KB governance report", "scripts/kb_governance_report.py"),
        _backend("safety rules report", "scripts/safety_rules_report.py"),
        _backend("OCR evaluation", "scripts/evaluate_ocr.py"),
        _backend("OCR provider report", "scripts/ocr_provider_report.py"),
        _backend("OCR candidate report", "scripts/ocr_candidate_report.py"),
        _backend("OCR activation policy report", "scripts/ocr_activation_policy_report.py"),
        _backend("E2E workflow evaluation", "scripts/evaluate_e2e_workflow.py"),
        _backend("export E2E traces", "scripts/export_e2e_traces.py"),
        _backend("E2E trace report", "scripts/e2e_trace_report.py"),
        _backend("Tesseract benchmark", "scripts/benchmark_tesseract_ocr.py", optional=True),
        _backend("project evidence report", "scripts/project_evidence_report.py"),
        _backend("final demo report", "scripts/final_demo_report.py"),
        QaCommand("frontend typecheck", ["npm.cmd", "run", "typecheck"], FRONTEND_ROOT),
        QaCommand("frontend build", ["npm.cmd", "run", "build"], FRONTEND_ROOT),
        QaCommand("git diff check", ["git", "diff", "--check"], REPO_ROOT),
    ]


def run_final_project_qa(list_only: bool = False) -> int:
    commands = build_qa_commands()
    if list_only:
        for command in commands:
            print(f"- {command.label}: {' '.join(command.command)} (cwd={command.cwd})")
        return 0

    failures = 0
    for command in commands:
        print(f"== {command.label} ==")
        result = subprocess.run(
            command.command,
            cwd=command.cwd,
            text=True,
            capture_output=True,
            check=False,
        )
        status = "PASS" if result.returncode == 0 else ("SKIP" if command.optional else "FAIL")
        print(f"{status}: {command.label} (exit={result.returncode})")
        if result.stdout.strip():
            print(_tail(result.stdout))
        if result.stderr.strip():
            print(_tail(result.stderr))
        if result.returncode != 0 and not command.optional:
            failures += 1
    print(f"Final QA status: {'PASS' if failures == 0 else 'FAIL'}")
    return 0 if failures == 0 else 1


def main() -> int:
    parser = argparse.ArgumentParser(description="Run PharmaGuard AI final QA commands.")
    parser.add_argument(
        "--list",
        action="store_true",
        help="List QA commands without executing them.",
    )
    args = parser.parse_args()
    return run_final_project_qa(list_only=args.list)


def _backend(label: str, script_path: str, optional: bool = False) -> QaCommand:
    return QaCommand(label, [sys.executable, script_path], BACKEND_ROOT, optional=optional)


def _tail(value: str, max_lines: int = 18) -> str:
    lines = value.strip().splitlines()
    selected = lines[-max_lines:]
    return "\n".join(selected)


if __name__ == "__main__":
    raise SystemExit(main())
