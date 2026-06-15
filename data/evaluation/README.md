# Evaluation

This directory contains synthetic evaluation templates and RAG evaluation cases.

Do not use real patient data. Evaluation cases must be fabricated, versioned, and reviewed for safety.

## RAG Evaluation

`rag_eval_cases.json` currently contains 20 synthetic cases covering:

- supported local drug profiles
- alias handling where the mock index supports it
- unknown medication names
- weak queries with no clear medication
- condition-only queries that must not map to arbitrary drugs
- unsupported-information requests
- exact-dose and final-advice prompts that must remain pharmacist-support only
- mixed prescription-like text with missing patient context language

Run from `backend/`:

```bash
python scripts/evaluate_rag.py
```

Metrics:

- `top_k_hit`: expected medication appears in retrieved context, or no random context is retrieved when none is expected.
- `source_file_hit`: expected Markdown files are retrieved.
- `section_hit`: expected source sections are retrieved.
- `insufficient_context_correct`: weak or unknown cases correctly return insufficient context.
- generation safety checks: required terms present, forbidden terms absent, draft/pharmacist-review framing present, unavailable information not invented, final-advice wording absent, and citations valid.

All evaluation content is synthetic and non-clinical.

Dense retrieval is deferred until this TF-IDF baseline has stronger coverage and known failure modes. OCR is still Phase 2 and is intentionally not part of RAG evaluation expansion.
