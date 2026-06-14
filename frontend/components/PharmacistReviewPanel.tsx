import { CheckCircle2, CircleAlert } from "lucide-react";

import type { PrescriptionAnalysisResponse } from "@/lib/types";

interface PharmacistReviewPanelProps {
  analysis: PrescriptionAnalysisResponse | null;
  isGenerating: boolean;
  onGenerateCounseling: () => void;
}

export function PharmacistReviewPanel({
  analysis,
  isGenerating,
  onGenerateCounseling
}: PharmacistReviewPanelProps) {
  const medications = analysis?.extracted_medications ?? [];
  const hasMedication = medications.length > 0;

  return (
    <section className="rounded-lg border border-pharma-line bg-white p-5 shadow-panel">
      <div className="mb-4 flex items-start justify-between gap-3">
        <div>
          <h2 className="text-lg font-semibold text-pharma-ink">Pharmacist Review</h2>
          <p className="text-sm text-pharma-muted">Draft extraction results</p>
        </div>
        <div className="rounded-md bg-pharma-mint px-2.5 py-1 text-xs font-semibold text-pharma-teal">
          Review required
        </div>
      </div>

      {analysis ? (
        <div className="space-y-4">
          <div className="flex items-center justify-between rounded-md border border-pharma-line px-3 py-2">
            <span className="text-sm text-pharma-muted">Confidence</span>
            <span className="text-sm font-semibold text-pharma-ink">
              {(analysis.confidence_score * 100).toFixed(0)}%
            </span>
          </div>

          <div className="space-y-3">
            {medications.map((medication) => (
              <div key={`${medication.name}-${medication.matched_text}`} className="rounded-md border border-pharma-line p-3">
                <div className="flex items-center gap-2">
                  <CheckCircle2 aria-hidden="true" size={17} className="text-pharma-emerald" />
                  <p className="font-semibold capitalize text-pharma-ink">{medication.name}</p>
                </div>
                <dl className="mt-3 grid gap-2 text-sm">
                  <div className="flex justify-between gap-3">
                    <dt className="text-pharma-muted">Strength</dt>
                    <dd className="text-right font-medium text-pharma-ink">{medication.strength ?? "Not extracted"}</dd>
                  </div>
                  <div className="flex justify-between gap-3">
                    <dt className="text-pharma-muted">Directions</dt>
                    <dd className="max-w-56 text-right font-medium text-pharma-ink">{medication.directions ?? "Not extracted"}</dd>
                  </div>
                </dl>
              </div>
            ))}
          </div>

          {!hasMedication && (
            <div className="flex gap-2 rounded-md border border-amber-200 bg-amber-50 p-3 text-sm text-pharma-amber">
              <CircleAlert aria-hidden="true" size={18} />
              <span>No local medication match was extracted.</span>
            </div>
          )}

          <button
            type="button"
            onClick={onGenerateCounseling}
            disabled={!hasMedication || isGenerating}
            className="inline-flex w-full items-center justify-center gap-2 rounded-md bg-pharma-emerald px-4 py-2.5 text-sm font-semibold text-white transition hover:bg-pharma-teal disabled:cursor-not-allowed disabled:bg-gray-300"
          >
            <CheckCircle2 aria-hidden="true" size={17} />
            {isGenerating ? "Generating draft" : "Confirm for counseling draft"}
          </button>
        </div>
      ) : (
        <div className="rounded-md border border-dashed border-pharma-line p-4 text-sm text-pharma-muted">
          Awaiting prescription analysis.
        </div>
      )}
    </section>
  );
}
