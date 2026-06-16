import subprocess
import sys
from pathlib import Path

from app.rag.retrieval_evaluation import evaluate_retrieval_strategies
from app.rag.retrieval_strategies import retrieve_with_strategy


def test_retrieval_strategies_return_source_backed_chunks() -> None:
    for strategy in ("existing_default", "lexical_overlap", "metadata_boosted", "hybrid_local"):
        contexts = retrieve_with_strategy(
            "paracetamol counseling",
            strategy_name=strategy,
            top_k=5,
        )

        assert contexts
        assert all(context.drug_name.lower() == "paracetamol" for context in contexts)
        assert all(context.strategy_name == strategy for context in contexts)
        assert all(context.source_file == "paracetamol.md" for context in contexts)
        assert all(context.source_status == "placeholder_educational" for context in contexts)


def test_retrieval_strategies_keep_unknown_queries_insufficient() -> None:
    for strategy in ("existing_default", "lexical_overlap", "metadata_boosted", "hybrid_local"):
        assert retrieve_with_strategy("xyzmed 20 mg counseling", strategy_name=strategy) == []


def test_retrieval_strategy_evaluation_passes_current_baseline() -> None:
    report = evaluate_retrieval_strategies()

    assert report["passed"] is True
    assert report["total_cases"] >= 46
    assert report["recommended_default_strategy"] == "existing_default"
    assert all(strategy["passed"] for strategy in report["strategies"])


def test_retrieval_strategy_report_script_runs() -> None:
    backend_root = Path(__file__).resolve().parents[1]
    result = subprocess.run(
        [sys.executable, "scripts/evaluate_retrieval_strategies.py"],
        cwd=backend_root,
        check=False,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0
    assert "recommended default strategy: existing_default" in result.stdout
    assert "overall status: PASS" in result.stdout
