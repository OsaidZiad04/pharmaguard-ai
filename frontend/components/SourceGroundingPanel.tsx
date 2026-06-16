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

  return (
    <section className="rounded-lg border border-pharma-line bg-white p-5 shadow-panel">
      <div className="mb-4 flex items-center gap-3">
        <div className="flex h-9 w-9 items-center justify-center rounded-md bg-pharma-mint text-pharma-teal">
          <DatabaseZap aria-hidden="true" size={18} />
        </div>
        <div>
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
        <div className="mt-4 flex gap-3 rounded-md border border-amber-200 bg-amber-50 p-3 text-sm text-amber-900">
          <FileWarning aria-hidden="true" className="mt-0.5 shrink-0" size={17} />
          <p>
            Insufficient local knowledge-base context is active. Medication-specific output must stay blocked
            or draft-only for pharmacist review.
          </p>
        </div>
      ) : chunks.length > 0 ? (
        <div className="mt-4 rounded-md border border-emerald-200 bg-emerald-50 p-3">
          <div className="mb-2 flex items-center gap-2 text-sm font-semibold text-pharma-teal">
            <BookOpenCheck aria-hidden="true" size={16} />
            Source grounding checked
          </div>
          <div className="flex flex-wrap gap-2">
            {sourceFiles.map((sourceFile) => (
              <span
                key={sourceFile}
                className="rounded-md border border-emerald-200 bg-white px-2.5 py-1 text-xs font-medium text-pharma-teal"
              >
                {sourceFile}
              </span>
            ))}
          </div>
        </div>
      ) : (
        <div className="mt-4 rounded-md border border-dashed border-pharma-line p-3 text-sm text-pharma-muted">
          Source grounding appears after prescription analysis finds a supported medication.
        </div>
      )}
    </section>
  );
}

function Metric({ label, value }: { label: string; value: string }) {
  return (
    <div className="rounded-md border border-pharma-line bg-pharma-wash p-3">
      <p className="text-xs font-medium uppercase text-pharma-muted">{label}</p>
      <p className="mt-1 text-xl font-semibold text-pharma-ink">{value}</p>
    </div>
  );
}
