import {
  AlertTriangle,
  CheckCircle2,
  ClipboardCheck,
  Database,
  FileText,
  ShieldCheck
} from "lucide-react";

const evidenceCards = [
  {
    label: "RAG Evaluation",
    value: "46/46",
    detail: "Synthetic retrieval and generation checks passed.",
    icon: Database
  },
  {
    label: "OCR Evaluation",
    value: "18/18",
    detail: "Synthetic OCR and fixture-backed cases passed.",
    icon: FileText
  },
  {
    label: "E2E Workflow",
    value: "10/10",
    detail: "Corrected-text boundary and source grounding passed.",
    icon: ClipboardCheck
  },
  {
    label: "Backend Tests",
    value: "177",
    detail: "Latest documented count: 177 passed, 1 skipped.",
    icon: CheckCircle2
  }
];

const governanceRows = [
  ["KB governance", "PASS, 0 blockers, draft warnings expected"],
  ["Retrieval strategy evaluation", "PASS, existing_default remains default"],
  ["Safety rules report", "PASS, pharmacist-review prompts only"],
  ["Tesseract status", "Optional, disabled by default, safe skip if unavailable"],
  ["Patient-facing output", "Disabled"],
  ["Clinical validation", "Not claimed"]
];

export default function EvaluationPage() {
  return (
    <main className="min-h-screen bg-pharma-bg px-4 py-6 text-pharma-ink sm:px-6 lg:px-8">
      <div className="mx-auto max-w-6xl space-y-6">
        <header className="rounded-lg border border-pharma-line bg-white p-6 shadow-panel">
          <div className="flex flex-col gap-4 md:flex-row md:items-center md:justify-between">
            <div>
              <p className="text-sm font-semibold uppercase text-pharma-teal">
                Project Evidence
              </p>
              <h1 className="mt-2 text-3xl font-semibold text-pharma-ink">
                PharmaGuard AI Evaluation Summary
              </h1>
              <p className="mt-3 max-w-3xl text-sm leading-6 text-pharma-muted">
                Static portfolio evidence for a pharmacist-centered prototype. These are
                engineering checks using synthetic data, not clinical validation.
              </p>
            </div>
            <div className="rounded-md border border-amber-200 bg-amber-50 p-3 text-sm text-amber-900">
              <div className="flex items-start gap-2">
                <AlertTriangle aria-hidden="true" className="mt-0.5 shrink-0" size={18} />
                <p>
                  Pharmacist review is mandatory. Patient-facing output is disabled.
                </p>
              </div>
            </div>
          </div>
        </header>

        <section className="grid gap-4 md:grid-cols-2 xl:grid-cols-4">
          {evidenceCards.map((card) => {
            const Icon = card.icon;
            return (
              <article key={card.label} className="rounded-lg border border-pharma-line bg-white p-5 shadow-panel">
                <div className="flex items-center justify-between">
                  <div className="flex h-10 w-10 items-center justify-center rounded-md bg-pharma-mint text-pharma-teal">
                    <Icon aria-hidden="true" size={20} />
                  </div>
                  <span className="rounded-md bg-emerald-50 px-2 py-1 text-xs font-semibold text-pharma-teal">
                    PASS
                  </span>
                </div>
                <p className="mt-4 text-sm font-medium text-pharma-muted">{card.label}</p>
                <p className="mt-1 text-3xl font-semibold text-pharma-ink">{card.value}</p>
                <p className="mt-2 text-sm leading-6 text-pharma-muted">{card.detail}</p>
              </article>
            );
          })}
        </section>

        <section className="grid gap-6 lg:grid-cols-[1.2fr_0.8fr]">
          <article className="rounded-lg border border-pharma-line bg-white p-6 shadow-panel">
            <div className="mb-4 flex items-center gap-3">
              <div className="flex h-10 w-10 items-center justify-center rounded-md bg-pharma-mint text-pharma-teal">
                <ShieldCheck aria-hidden="true" size={20} />
              </div>
              <div>
                <h2 className="text-xl font-semibold">Governance & Safety Status</h2>
                <p className="text-sm text-pharma-muted">Prototype boundaries</p>
              </div>
            </div>
            <div className="divide-y divide-pharma-line rounded-md border border-pharma-line">
              {governanceRows.map(([label, value]) => (
                <div key={label} className="grid gap-2 p-3 sm:grid-cols-[220px_1fr]">
                  <p className="text-sm font-semibold text-pharma-ink">{label}</p>
                  <p className="text-sm leading-6 text-pharma-muted">{value}</p>
                </div>
              ))}
            </div>
          </article>

          <aside className="rounded-lg border border-pharma-line bg-white p-6 shadow-panel">
            <h2 className="text-xl font-semibold">Demo Readiness</h2>
            <ul className="mt-4 space-y-3 text-sm leading-6 text-pharma-muted">
              <li>Use synthetic demo cases only.</li>
              <li>Show OCR correction before analysis.</li>
              <li>Show source grounding and KB governance.</li>
              <li>Show safety rules as review prompts.</li>
              <li>State limitations clearly.</li>
            </ul>
          </aside>
        </section>
      </div>
    </main>
  );
}
