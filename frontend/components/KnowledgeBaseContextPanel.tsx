import { DatabaseZap } from "lucide-react";

import type { RetrievedChunk } from "@/lib/types";

interface KnowledgeBaseContextPanelProps {
  chunks: RetrievedChunk[];
}

export function KnowledgeBaseContextPanel({ chunks }: KnowledgeBaseContextPanelProps) {
  return (
    <section className="rounded-lg border border-pharma-line bg-white p-5 shadow-panel">
      <div className="mb-4 flex items-center gap-3">
        <div className="flex h-9 w-9 items-center justify-center rounded-md bg-pharma-mint text-pharma-teal">
          <DatabaseZap aria-hidden="true" size={18} />
        </div>
        <div>
          <h2 className="text-lg font-semibold text-pharma-ink">Knowledge Base Context</h2>
          <p className="text-sm text-pharma-muted">Local Markdown retrieval</p>
        </div>
      </div>

      {chunks.length > 0 ? (
        <div className="space-y-3">
          {chunks.slice(0, 5).map((chunk) => (
            <article key={chunk.chunk_id} className="rounded-md border border-pharma-line p-3">
              <div className="mb-2 flex flex-wrap items-center gap-2 text-xs">
                <span className="rounded-md bg-pharma-mint px-2 py-1 font-semibold text-pharma-teal">
                  {chunk.source_file}
                </span>
                <span className="rounded-md bg-pharma-wash px-2 py-1 font-medium text-pharma-muted">
                  {chunk.section_title}
                </span>
                {chunk.source_status ? (
                  <span className="rounded-md bg-amber-50 px-2 py-1 font-medium text-amber-800">
                    {formatStatus(chunk.source_status)}
                  </span>
                ) : null}
                {chunk.clinical_validation_status ? (
                  <span className="rounded-md bg-pharma-wash px-2 py-1 font-medium text-pharma-muted">
                    {formatStatus(chunk.clinical_validation_status)}
                  </span>
                ) : null}
                <span className="ml-auto font-semibold text-pharma-ink">
                  {chunk.score.toFixed(3)}
                </span>
              </div>
              <p className="line-clamp-4 text-sm leading-6 text-pharma-muted">{chunk.text}</p>
            </article>
          ))}
        </div>
      ) : (
        <div className="rounded-md border border-dashed border-pharma-line p-4 text-sm text-pharma-muted">
          Retrieved chunks appear after a matched medication is reviewed.
        </div>
      )}
    </section>
  );
}

function formatStatus(value: string) {
  return value.replaceAll("_", " ");
}
