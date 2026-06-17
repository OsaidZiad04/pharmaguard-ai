import { BookOpenCheck, DatabaseZap, FileWarning } from "lucide-react";

import type { RetrievedChunk } from "@/lib/types";

interface SourceGroundingPanelProps {
  chunks: RetrievedChunk[];
  insufficientContext: boolean;
}

export function SourceGroundingPanel({
  chunks,
  insufficientContext
}: SourceGroundingPanelProps) {
  const sourceFiles = Array.from(new Set(chunks.map((chunk) => chunk.source_file)));
  const sectionTitles = Array.from(new Set(chunks.map((chunk) => chunk.section_title)));
  const sourceStatuses = Array.from(
    new Set(chunks.map((chunk) => chunk.source_status).filter(isNonEmptyStatus))
  );
  const validationStatuses = Array.from(
    new Set(
      chunks.map((chunk) => chunk.clinical_validation_status).filter(isNonEmptyStatus)
    )
  );

  return (
    <section className="pg-card rounded-2xl p-5">
      <div className="mb-4 flex items-center gap-3">
        <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-pharma-mint text-pharma-teal">
          <DatabaseZap aria-hidden="true" size={18} />
        </div>
        <div>
          <p className="text-xs font-semibold uppercase text-pharma-teal">Source grounding</p>
          <h2 className="text-lg font-semibold text-pharma-ink">Source Grounding</h2>
          <p className="text-sm text-pharma-muted">Local Markdown context status</p>
        </div>
      </div>

      <div className="grid gap-3 sm:grid-cols-3">
        <Metric label="Retrieved chunks" value={String(chunks.length)} />
        <Metric label="Source files" value={String(sourceFiles.length)} />
        <Metric label="Sections" value={String(sectionTitles.length)} />
      </div>

      {insufficientContext ? (
        <div className="mt-4 flex gap-3 rounded-xl border border-amber-200 bg-amber-50 p-3 text-sm text-amber-900">
          <FileWarning aria-hidden="true" className="mt-0.5 shrink-0" size={17} />
          <p>
            Insufficient local knowledge-base context is active. Medication-specific output must stay blocked
            or draft-only for pharmacist review.
          </p>
        </div>
      ) : chunks.length > 0 ? (
        <div className="mt-4 rounded-xl border border-emerald-200 bg-emerald-50 p-3">
          <div className="mb-2 flex items-center gap-2 text-sm font-semibold text-pharma-teal">
            <BookOpenCheck aria-hidden="true" size={16} />
            Source grounding checked
          </div>
          <div className="flex flex-wrap gap-2">
            {sourceFiles.map((sourceFile) => (
              <span
                key={sourceFile}
                className="rounded-full border border-emerald-200 bg-white px-2.5 py-1 text-xs font-medium text-pharma-teal"
              >
                {sourceFile}
              </span>
            ))}
            {sourceStatuses.map((status) => (
              <span
                key={status}
                className="rounded-full border border-amber-200 bg-white px-2.5 py-1 text-xs font-medium text-amber-800"
              >
                {formatStatus(status)}
              </span>
            ))}
            {validationStatuses.map((status) => (
              <span
                key={status}
                className="rounded-full border border-pharma-line bg-white px-2.5 py-1 text-xs font-medium text-pharma-muted"
              >
                {formatStatus(status)}
              </span>
            ))}
          </div>
        </div>
      ) : (
        <div className="mt-4 rounded-xl border border-dashed border-pharma-line bg-white/70 p-3 text-sm text-pharma-muted">
          Source grounding appears after prescription analysis finds a supported medication.
        </div>
      )}
    </section>
  );
}

function formatStatus(value: string) {
  return value.replaceAll("_", " ");
}

function isNonEmptyStatus(value: string | null | undefined): value is string {
  return Boolean(value);
}

function Metric({ label, value }: { label: string; value: string }) {
  return (
    <div className="rounded-xl border border-pharma-line bg-white p-3 shadow-sm">
      <p className="text-xs font-medium uppercase text-pharma-muted">{label}</p>
      <p className="mt-1 text-xl font-semibold text-pharma-ink">{value}</p>
    </div>
  );
}
