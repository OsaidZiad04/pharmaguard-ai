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
    <section className="rounded-lg border border-pharma-line bg-white p-5 shadow-panel">
      <div className="mb-4 flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
        <div>
          <h2 className="text-lg font-semibold text-pharma-ink">Prescription Text</h2>
          <p className="text-sm text-pharma-muted">Synthetic text only</p>
        </div>
        <button
          type="button"
          onClick={onLoadSample}
          className="inline-flex items-center justify-center gap-2 rounded-md border border-pharma-line px-3 py-2 text-sm font-medium text-pharma-ink transition hover:border-pharma-teal hover:text-pharma-teal"
        >
          <ClipboardCheck aria-hidden="true" size={16} />
          Load sample
        </button>
      </div>

      <textarea
        value={value}
        onChange={(event) => onChange(event.target.value)}
        rows={9}
        className="min-h-56 w-full rounded-md border border-pharma-line bg-white p-4 text-sm leading-6 text-pharma-ink outline-none transition placeholder:text-gray-400 focus:border-pharma-teal focus:ring-2 focus:ring-emerald-100"
        placeholder="Paste synthetic prescription text for pharmacist review."
      />

      <div className="mt-4 flex justify-end">
        <button
          type="button"
          onClick={onAnalyze}
          disabled={isLoading || value.trim().length === 0}
          className="inline-flex min-w-36 items-center justify-center gap-2 rounded-md bg-pharma-teal px-4 py-2.5 text-sm font-semibold text-white transition hover:bg-emerald-700 disabled:cursor-not-allowed disabled:bg-gray-300"
        >
          <Search aria-hidden="true" size={17} />
          {isLoading ? "Analyzing" : "Analyze text"}
        </button>
      </div>
    </section>
  );
}
