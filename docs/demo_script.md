# Demo Script

## Five-Minute Demo

1. Open the pharmacist dashboard.
   - Say: "This is a pharmacist-centered prototype, not a clinical decision engine."

2. Show OCR intake.
   - Upload or reference a synthetic fixture.
   - Say: "OCR is unverified and cannot go downstream until corrected."

3. Correct the OCR text.
   - Use the corrected text action.
   - Say: "The pharmacist correction boundary is explicit."

4. Run prescription analysis.
   - Show extracted medications and safety findings.
   - Say: "Safety rules are review prompts, not medical decisions."

5. Show RAG source grounding.
   - Point to local Markdown source files, sections, scores, and governance badges.
   - Say: "The knowledge base is draft placeholder educational content and not clinically validated."

6. Show counseling draft.
   - Say: "Counseling remains draft-only and pharmacist-review-required."

7. Close with evidence.
   - Mention RAG 46/46, OCR 18/18, E2E 10/10, backend tests, KB governance, and safety rules.

## Ten-Minute Demo

Use the five-minute flow, then add:

1. Unsupported medication case.
   - Show insufficient context and no guessing.

2. Multiple medication case.
   - Show multiple-medication prompt and interaction-check-unavailable boundary.

3. Possible identifier case.
   - Show warning language: possible identifiers, not confirmed PII.

4. Evaluation page or project evidence report.
   - Show how the project is evaluation-driven and governance-aware.

## Fallback If Tesseract Is Unavailable

Say: "Tesseract is intentionally optional and disabled by default. On this machine the benchmark may skip if the binary is unavailable, and that is a safe outcome. The default OCR workflow remains mock/synthetic and correction-gated."

## Safety Talking Points

- Pharmacist review is mandatory.
- Patient-facing output is disabled.
- The current KB is draft placeholder content.
- The project does not validate interactions, contraindications, diagnoses, or treatment decisions.
- All demo data is synthetic.
