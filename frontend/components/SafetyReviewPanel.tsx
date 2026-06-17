import {
  AlertTriangle,
  CheckCircle2,
  FileWarning,
  LockKeyhole,
  ShieldCheck
} from "lucide-react";

interface SafetyReviewPanelProps {
  ocrUnverified: boolean;
  correctionRequired: boolean;
  correctedTextReady: boolean;
  possibleIdentifierWarningCount: number;
  ragSourcesAvailable: boolean;
  insufficientKnowledgeBaseContext: boolean;
  counselingDraftReady: boolean;
  pharmacistReviewRequired: boolean;
}

export function SafetyReviewPanel({
  ocrUnverified,
  correctionRequired,
  correctedTextReady,
  possibleIdentifierWarningCount,
  ragSourcesAvailable,
  insufficientKnowledgeBaseContext,
  counselingDraftReady,
  pharmacistReviewRequired
}: SafetyReviewPanelProps) {
  const indicators = [
    {
      label: "OCR unverified",
      active: ocrUnverified,
      tone: "warning",
      detail: "OCR text is assistive only."
    },
    {
      label: "Correction required",
      active: correctionRequired,
      tone: correctionRequired ? "warning" : "ready",
      detail: correctedTextReady ? "Corrected text is ready." : "Confirm OCR before analysis."
    },
    {
      label: "Possible identifiers",
      active: possibleIdentifierWarningCount > 0,
      tone: possibleIdentifierWarningCount > 0 ? "warning" : "ready",
      detail:
        possibleIdentifierWarningCount > 0
          ? `${possibleIdentifierWarningCount} warning category detected.`
          : "No OCR privacy warning returned."
    },
    {
      label: "RAG sources",
      active: ragSourcesAvailable,
      tone: ragSourcesAvailable ? "ready" : "waiting",
      detail: ragSourcesAvailable ? "Local sources retrieved." : "Awaiting matched medication."
    },
    {
      label: "KB context",
      active: insufficientKnowledgeBaseContext,
      tone: insufficientKnowledgeBaseContext ? "blocked" : "ready",
      detail: insufficientKnowledgeBaseContext
        ? "Insufficient context warning active."
        : "No insufficient-context warning active."
    },
    {
      label: "Counseling draft",
      active: counselingDraftReady,
      tone: counselingDraftReady ? "ready" : "waiting",
      detail: counselingDraftReady ? "Draft-only counseling visible." : "Generated after confirmation."
    },
    {
      label: "Pharmacist review",
      active: pharmacistReviewRequired,
      tone: "warning",
      detail: "Required before patient-facing use."
    }
  ] as const;

  return (
    <section className="pg-card rounded-2xl p-5">
      <div className="mb-4 flex items-center gap-3">
        <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-amber-50 text-amber-700">
          <ShieldCheck aria-hidden="true" size={18} />
        </div>
        <div>
          <p className="text-xs font-semibold uppercase text-pharma-teal">Guardrail map</p>
          <h2 className="text-lg font-semibold text-pharma-ink">Safety Review</h2>
          <p className="text-sm text-pharma-muted">Workflow guardrails</p>
        </div>
      </div>

      <div className="grid gap-3 sm:grid-cols-2">
        {indicators.map((indicator) => (
          <div
            key={indicator.label}
            className="flex gap-3 rounded-xl border border-pharma-line bg-white p-3 shadow-sm"
          >
            <span className={indicatorIconClassName(indicator.tone)}>
              {indicator.tone === "blocked" ? (
                <AlertTriangle aria-hidden="true" size={16} />
              ) : indicator.tone === "warning" ? (
                <FileWarning aria-hidden="true" size={16} />
              ) : indicator.tone === "ready" ? (
                <CheckCircle2 aria-hidden="true" size={16} />
              ) : (
                <LockKeyhole aria-hidden="true" size={16} />
              )}
            </span>
            <div>
              <p className="text-sm font-semibold text-pharma-ink">{indicator.label}</p>
              <p className="mt-1 text-xs leading-5 text-pharma-muted">{indicator.detail}</p>
            </div>
          </div>
        ))}
      </div>
    </section>
  );
}

function indicatorIconClassName(tone: "warning" | "ready" | "blocked" | "waiting") {
  const base = "mt-0.5 inline-flex h-8 w-8 shrink-0 items-center justify-center rounded-xl";
  if (tone === "ready") {
    return `${base} bg-emerald-100 text-pharma-teal`;
  }
  if (tone === "blocked") {
    return `${base} bg-red-50 text-red-700`;
  }
  if (tone === "warning") {
    return `${base} bg-amber-50 text-amber-700`;
  }
  return `${base} bg-white text-pharma-muted`;
}
