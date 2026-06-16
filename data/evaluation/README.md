# Evaluation

This directory contains synthetic evaluation templates, RAG evaluation cases, and OCR evaluation cases.

Do not use real patient data. Evaluation cases must be fabricated, versioned, and reviewed for safety.

## RAG Evaluation

`rag_eval_cases.json` currently contains 46 synthetic cases covering:

- supported local drug profiles
- alias handling from the drug registry, with the mock index retained as compatibility fallback
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

Phase 3B adds retrieval strategy comparison around the same RAG evaluation baseline. Run from `backend/`:

```bash
python scripts/evaluate_retrieval_strategies.py
```

The report compares the existing default retriever with local lexical, metadata-boosted, and hybrid strategies. It is an engineering benchmark only; it does not validate clinical relevance.

Phase 1.8 adds KB registry and validation checks around the same evaluation baseline. Run the KB coverage report from `backend/`:

```bash
python scripts/kb_report.py
```

Dense retrieval is deferred until this TF-IDF baseline and registry governance have stronger coverage and known failure modes. OCR is still Phase 2 and is intentionally not part of scalable knowledge base architecture work.

## OCR Evaluation

`ocr_eval_cases.json` contains 18 synthetic OCR cases covering clean OCR, noisy medication text, low-confidence text, possible identifier labels, phone-like numbers, clinic labels, supported and unsupported medication names, multiple medication terms, ambiguous handwriting-like errors represented as text, and no-medication cases. Phase 2C and Phase 2D add fixture-backed cases through `fixture_filename` values that point to approved synthetic PNG files or descriptor fixtures in `ocr_fixtures/`.

Run from `backend/`:

```bash
python scripts/evaluate_ocr.py
```

Metrics:

- `character_error_rate`: edit distance between expected corrected text and mock OCR text, normalized by reference characters.
- `word_error_rate`: token edit distance between expected corrected text and mock OCR text.
- `token_overlap_score`: deterministic token overlap between expected corrected text and mock OCR text.
- `medication_detection_hit`: expected medication terms appear in corrected synthetic text, or no supported medication is inferred when none is expected.
- `privacy_warning_match`: expected possible identifier categories match detected categories.

These metrics are synthetic engineering checks for OCR workflow readiness. They are not clinical validation and do not certify production OCR quality.

## End-to-End Workflow Evaluation

`e2e_workflow_cases.json` contains 10 synthetic OCR-to-RAG workflow cases covering clean supported medication text, noisy OCR correction, multiple supported medications, supported plus unsupported medication-like text, unknown medication, possible identifier warnings, no medication detected, exact-dose prompts, final-advice prompts, and fixture-backed OCR.

Run from `backend/`:

```bash
python scripts/evaluate_e2e_workflow.py
```

The evaluator verifies that unverified OCR does not go downstream automatically, pharmacist-corrected text can move into prescription analysis, supported medications retrieve source-backed RAG context, unknown medications remain insufficient context, and counseling drafts remain pharmacist-support only. It is synthetic workflow evaluation, not clinical validation.

## Generated Workflow Traces

`generated/e2e_traces.json` contains deterministic synthetic trace records generated from `e2e_workflow_cases.json`.

Regenerate from `backend/`:

```bash
python scripts/export_e2e_traces.py
```

Trace records contain step summaries, source references, safety flags, and pharmacist review metadata. They do not contain raw image bytes, real prescription images, real patient data, or production audit logs.

## Medication Safety Rules Report

Phase 3C adds deterministic synthetic safety-rule scenarios. Run from `backend/`:

```bash
python scripts/safety_rules_report.py
```

The report checks missing prescription fields, unsupported/no medication text, possible identifiers, placeholder KB context, not-clinically-validated profiles, pharmacist review requirements, and patient-facing output blocks. These are workflow safety prompts, not clinical validation.
