import { ClipboardCheck, Search } from "lucide-react";

interface PrescriptionIntakeCardProps {
  value: string;
  isLoading: boolean;
  onChange: (value: string) => void;
  onAnalyze: () => void;
  onLoadSample: () => void;
}

export function PrescriptionIntakeCard({
  value,
  isLoading,
  onChange,
  onAnalyze,
  onLoadSample
}: PrescriptionIntakeCardProps) {
  return (
    <section className="pg-card rounded-2xl p-5">
      <div className="mb-4 flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
        <div>
          <p className="text-xs font-semibold uppercase text-pharma-teal">Prescription desk</p>
          <h2 className="text-lg font-semibold text-pharma-ink">Prescription Text</h2>
          <p className="text-sm text-pharma-muted">Synthetic text only</p>
        </div>
        <button
          type="button"
          onClick={onLoadSample}
          className="inline-flex items-center justify-center gap-2 rounded-xl border border-pharma-line bg-white px-3 py-2 text-sm font-medium text-pharma-ink shadow-sm transition hover:border-pharma-teal hover:text-pharma-teal"
        >
          <ClipboardCheck aria-hidden="true" size={16} />
          Load sample
        </button>
      </div>

      <textarea
        value={value}
        onChange={(event) => onChange(event.target.value)}
        rows={9}
        className="min-h-56 w-full rounded-2xl border border-pharma-line bg-white p-4 text-sm leading-6 text-pharma-ink shadow-inner outline-none transition placeholder:text-slate-400 focus:border-pharma-teal focus:ring-2 focus:ring-emerald-100"
        placeholder="Paste synthetic prescription text for pharmacist review."
      />

      <div className="mt-4 flex justify-end">
        <button
          type="button"
          onClick={onAnalyze}
          disabled={isLoading || value.trim().length === 0}
          className="inline-flex min-w-36 items-center justify-center gap-2 rounded-xl bg-pharma-teal px-4 py-2.5 text-sm font-semibold text-white shadow-sm transition hover:bg-emerald-700 disabled:cursor-not-allowed disabled:bg-slate-300"
        >
          <Search aria-hidden="true" size={17} />
          {isLoading ? "Analyzing" : "Analyze text"}
        </button>
      </div>
    </section>
  );
}
