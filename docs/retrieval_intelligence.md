# Retrieval Intelligence

Phase 3B adds local retrieval intelligence around the existing TF-IDF RAG pipeline. It does not replace the production retriever and does not add external embeddings, model downloads, or vector databases.

## Scope

Added backend modules:

- `backend/app/rag/retrieval_strategies.py`
- `backend/app/rag/retrieval_diagnostics.py`
- `backend/app/rag/query_classifier.py`
- `backend/app/rag/retrieval_evaluation.py`
- `backend/scripts/evaluate_retrieval_strategies.py`

## Retrieval Strategies

The current production strategy remains `existing_default`, which wraps the existing medication-aware TF-IDF retriever.

Diagnostic comparison strategies:

- `lexical_overlap`: token overlap against local chunks after explicit medication matching.
- `metadata_boosted`: lexical overlap plus simple section and metadata boosts.
- `hybrid_local`: combines current TF-IDF results with metadata-boosted fallback.

These strategies are local and deterministic. They are benchmarked, not automatically promoted.

## Query Classification

`query_classifier.py` classifies queries into:

- `drug_lookup`
- `counseling_request`
- `safety_check`
- `dose_frequency_check`
- `multiple_medication_review`
- `unsupported_or_unknown`
- `general_or_ambiguous`

The classifier is deterministic and registry-based. It does not infer medications from broad conditions or drug classes.

## Retrieval Diagnostics

Diagnostics identify:

- no context retrieved
- weak or sparse context
- single-source retrieval
- placeholder-only knowledge
- draft or unvalidated source material
- missing governance metadata
- mixed medication retrieval
- pharmacist-review-required sources

RAG query and drug-card responses can include `retrieval_diagnostics` as additive metadata.

## Strategy Evaluation

Run from `backend/`:

```bash
python scripts/evaluate_retrieval_strategies.py
```

The report compares strategies on:

- top-k medication hit rate
- expected source hit rate
- expected section hit rate
- insufficient-context correctness
- governance metadata presence
- weak retrieval detection
- average retrieved chunks

The report is an engineering benchmark only. It is not clinical validation and does not prove source correctness.

## Current Policy

`existing_default` remains the recommended default strategy. Any future retriever change must preserve unknown-medication insufficient-context behavior, citation validation, pharmacist review framing, and governance metadata.
