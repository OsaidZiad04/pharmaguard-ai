import { BookOpenCheck } from "lucide-react";

import type { DrugLookupResponse } from "@/lib/types";

interface DrugInfoCardProps {
  lookup: DrugLookupResponse | null;
}

export function DrugInfoCard({ lookup }: DrugInfoCardProps) {
  const drug = lookup?.drug;

  return (
    <section className="rounded-lg border border-pharma-line bg-white p-5 shadow-panel">
      <div className="mb-4 flex items-center gap-3">
        <div className="flex h-9 w-9 items-center justify-center rounded-md bg-pharma-mint text-pharma-teal">
          <BookOpenCheck aria-hidden="true" size={18} />
        </div>
        <div>
          <h2 className="text-lg font-semibold text-pharma-ink">Drug Information</h2>
          <p className="text-sm text-pharma-muted">Local mock index</p>
        </div>
      </div>

      {drug ? (
        <div className="space-y-4">
          <div>
            <p className="text-xl font-semibold text-pharma-ink">{drug.name}</p>
            <p className="text-sm text-pharma-muted">{drug.category}</p>
          </div>

          <InfoList title="Pharmacist notes" items={drug.pharmacist_notes} />
          <InfoList title="Counseling topics" items={drug.counseling_points} />
          <InfoList title="Safety considerations" items={drug.safety_considerations} />
        </div>
      ) : (
        <div className="rounded-md border border-dashed border-pharma-line p-4 text-sm text-pharma-muted">
          {lookup?.found === false ? "No local profile matched." : "Drug card appears after analysis."}
        </div>
      )}
    </section>
  );
}

function InfoList({ title, items }: { title: string; items: string[] }) {
  return (
    <div>
      <h3 className="mb-2 text-sm font-semibold text-pharma-ink">{title}</h3>
      <ul className="space-y-2 text-sm text-pharma-muted">
        {items.map((item) => (
          <li key={item} className="rounded-md bg-pharma-wash px-3 py-2">
            {item}
          </li>
        ))}
      </ul>
    </div>
  );
}
