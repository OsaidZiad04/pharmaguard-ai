import { FileText } from "lucide-react";

import type { CounselingResponse } from "@/lib/types";

interface PatientCounselingSheetProps {
  counseling: CounselingResponse | null;
}

export function PatientCounselingSheet({ counseling }: PatientCounselingSheetProps) {
  return (
    <section className="rounded-lg border border-pharma-line bg-white p-5 shadow-panel">
      <div className="mb-4 flex items-center gap-3">
        <div className="flex h-9 w-9 items-center justify-center rounded-md bg-pharma-mint text-pharma-teal">
          <FileText aria-hidden="true" size={18} />
        </div>
        <div>
          <h2 className="text-lg font-semibold text-pharma-ink">Patient Counseling Draft</h2>
          <p className="text-sm text-pharma-muted">Generated after pharmacist confirmation</p>
        </div>
      </div>

      {counseling ? (
        <div className="rounded-md border border-emerald-200 bg-emerald-50 p-4 text-sm leading-6 text-pharma-ink">
          {counseling.counseling_note}
        </div>
      ) : (
        <div className="rounded-md border border-dashed border-pharma-line p-4 text-sm text-pharma-muted">
          Counseling draft is empty.
        </div>
      )}
    </section>
  );
}
