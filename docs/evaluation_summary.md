# Evaluation Summary

All evaluations use synthetic data and engineering checks. They do not establish clinical validation, production readiness, or medical correctness.

## Latest Known Results

- Backend tests: 177 passed, 1 skipped.
- RAG evaluation: 46/46 passed.
- Retrieval strategy evaluation: PASS, recommended default `existing_default`.
- KB report: PASS, 15 profiles, 0 blockers.
- KB governance report: PASS, 0 blockers, expected draft warnings.
- Safety rules report: PASS, 10/10 synthetic scenarios.
- OCR evaluation: 18/18 passed.
- OCR provider report: PASS.
- OCR candidate report: PASS.
- OCR activation policy report: PASS.
- E2E OCR-to-RAG workflow evaluation: 10/10 passed.
- Trace export/report: PASS, 10 synthetic traces.
- Tesseract benchmark: optional; completes or safely skips when dependency is unavailable.
- Frontend typecheck/build: PASS.

## Evaluation Commands

Run from `backend/` unless noted:

```bash
python -m pytest
python scripts/evaluate_rag.py
python scripts/evaluate_retrieval_strategies.py
python scripts/kb_report.py
python scripts/kb_governance_report.py
python scripts/safety_rules_report.py
python scripts/evaluate_ocr.py
python scripts/ocr_provider_report.py
python scripts/ocr_candidate_report.py
python scripts/ocr_activation_policy_report.py
python scripts/evaluate_e2e_workflow.py
python scripts/export_e2e_traces.py
python scripts/e2e_trace_report.py
python scripts/benchmark_tesseract_ocr.py
python scripts/project_evidence_report.py
python scripts/final_demo_report.py
```

Run from `frontend/`:

```bash
npm.cmd run typecheck
npm.cmd run build
```

## Interpretation

Passing reports mean the prototype follows its synthetic safety and engineering requirements. They do not mean the knowledge base is clinically valid, complete, or approved for patient-facing use.
