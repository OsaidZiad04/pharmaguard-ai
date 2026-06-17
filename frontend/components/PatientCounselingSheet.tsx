import { FileText, ShieldCheck } from "lucide-react";

import type { CounselingResponse, RetrievedChunk } from "@/lib/types";

interface PatientCounselingSheetProps {
  counseling: CounselingResponse | null;
}

export function PatientCounselingSheet({ counseling }: PatientCounselingSheetProps) {
  return (
    <section className="pg-card rounded-2xl p-5">
      <div className="mb-4 flex items-center gap-3">
        <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-pharma-mint text-pharma-teal">
          <FileText aria-hidden="true" size={18} />
        </div>
        <div>
          <p className="text-xs font-semibold uppercase text-pharma-teal">Draft output</p>
          <h2 className="text-lg font-semibold text-pharma-ink">Patient Counseling Draft</h2>
          <p className="text-sm text-pharma-muted">Generated after pharmacist confirmation</p>
        </div>
      </div>

      {counseling ? (
        <div className="space-y-4">
          <div className="flex flex-wrap gap-2 text-xs font-semibold">
            <span className="inline-flex items-center gap-1 rounded-full bg-pharma-mint px-2.5 py-1 text-pharma-teal">
              <FileText aria-hidden="true" size={14} />
              Draft only
            </span>
            <span className="inline-flex items-center gap-1 rounded-full bg-amber-50 px-2.5 py-1 text-amber-800">
              <ShieldCheck aria-hidden="true" size={14} />
              Pharmacist review required
            </span>
          </div>
          <div className="whitespace-pre-wrap rounded-xl border border-emerald-200 bg-emerald-50 p-4 text-sm leading-6 text-pharma-ink shadow-inner">
            {counseling.counseling_note}
          </div>
          <CounselingSources sources={counseling.retrieved_sources} />
        </div>
      ) : (
        <div className="rounded-xl border border-dashed border-pharma-line bg-white/70 p-4 text-sm text-pharma-muted">
          Counseling draft is empty.
        </div>
      )}
    </section>
  );
}

function CounselingSources({ sources }: { sources: RetrievedChunk[] }) {
  return (
    <div>
      <h3 className="mb-2 text-sm font-semibold text-pharma-ink">Retrieved source files and sections</h3>
      {sources.length > 0 ? (
        <div className="flex flex-wrap gap-2">
          {sources.map((source) => (
            <span
              key={source.chunk_id}
              className="rounded-full border border-emerald-200 bg-white px-2.5 py-1 text-xs font-medium text-pharma-teal"
            >
              {source.source_file} / {source.section_title} / {source.score.toFixed(3)}
            </span>
          ))}
        </div>
      ) : (
        <p className="rounded-xl border border-dashed border-pharma-line bg-white/70 p-3 text-sm text-pharma-muted">
          No retrieved source passed the local relevance threshold.
        </p>
      )}
    </div>
  );
}
