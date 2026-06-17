import Link from "next/link";
import {
  AlertTriangle,
  CheckCircle2,
  ClipboardCheck,
  Database,
  FileText,
  FlaskConical,
  ShieldCheck
} from "lucide-react";

import { AppHeader } from "@/components/AppHeader";

const evidenceCards = [
  {
    label: "RAG Evaluation",
    value: "46/46",
    detail: "Synthetic retrieval and grounded-generation checks passed.",
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
  ["Retrieval strategy evaluation", "PASS, existing_default remains default"],
  ["Safety rules report", "PASS, pharmacist-review prompts only"],
  ["KB governance", "PASS, 0 blockers, draft warnings expected"],
  ["Tesseract status", "Optional, disabled by default, safe skip if unavailable"],
  ["Patient-facing output", "Disabled"],
  ["Pharmacist review", "Required"],
  ["Clinical validation", "Not claimed"],
  ["Current KB", "Draft placeholder educational content"]
];

const readinessItems = [
  "Use synthetic demo cases only.",
  "Show OCR correction before analysis.",
  "Show source grounding and KB governance.",
  "Show safety rules as review prompts.",
  "State limitations clearly."
];

export default function EvaluationPage() {
  return (
    <main className="pg-app-bg min-h-screen text-pharma-ink">
      <AppHeader />
      <div className="mx-auto max-w-7xl space-y-6 px-4 py-5 sm:px-6 lg:px-8">
        <header className="relative overflow-hidden rounded-2xl border border-white/80 bg-pharma-slate text-white shadow-command">
          <div className="absolute inset-0 bg-[radial-gradient(circle_at_20%_20%,rgba(16,185,129,0.28),transparent_34%),radial-gradient(circle_at_82%_18%,rgba(20,184,166,0.18),transparent_26%)]" />
          <div className="relative grid gap-6 p-6 lg:grid-cols-[1fr_360px] lg:p-8">
            <div>
              <div className="mb-5 inline-flex items-center gap-3 rounded-2xl border border-white/12 bg-white px-3 py-2">
                <img
                  src="/brand/pharmaguard-logo-main.png"
                  alt="PharmaGuard AI"
                  className="h-12 max-w-64 object-contain"
                />
              </div>
              <p className="text-sm font-semibold uppercase text-emerald-200">
                Project evidence dashboard
              </p>
              <h1 className="mt-3 max-w-3xl text-3xl font-semibold leading-tight sm:text-4xl">
                Evaluation evidence for a pharmacist-centered prototype.
              </h1>
              <p className="mt-4 max-w-3xl text-sm leading-6 text-emerald-50/85 sm:text-base">
                Static portfolio summary for synthetic engineering checks. These results do
                not establish clinical validation, medical-device readiness, or patient-facing
                advice.
              </p>
              <div className="mt-5 flex flex-wrap gap-2 text-xs font-semibold">
                <span className="rounded-full border border-emerald-300/40 bg-emerald-300/10 px-3 py-1.5 text-emerald-100">
                  Pharmacist review required
                </span>
                <span className="rounded-full border border-amber-300/50 bg-amber-300/10 px-3 py-1.5 text-amber-100">
                  Patient-facing output disabled
                </span>
                <span className="rounded-full border border-white/20 bg-white/10 px-3 py-1.5 text-white">
                  Not clinically validated
                </span>
              </div>
            </div>

            <aside className="rounded-2xl border border-white/12 bg-white/10 p-5 backdrop-blur">
              <div className="flex items-center gap-3">
                <div className="flex h-11 w-11 items-center justify-center rounded-xl bg-emerald-300/15 text-emerald-200">
                  <FlaskConical aria-hidden="true" size={22} />
                </div>
                <div>
                  <h2 className="font-semibold">Demo readiness</h2>
                  <p className="text-sm text-emerald-50/75">Synthetic evidence only</p>
                </div>
              </div>
              <Link
                href="/"
                className="mt-5 inline-flex w-full items-center justify-center rounded-xl bg-white px-4 py-2.5 text-sm font-semibold text-pharma-slate transition hover:bg-emerald-50"
              >
                Back to dashboard
              </Link>
            </aside>
          </div>
        </header>

        <section className="grid gap-4 md:grid-cols-2 xl:grid-cols-4">
          {evidenceCards.map((card) => {
            const Icon = card.icon;
            return (
              <article key={card.label} className="pg-card rounded-2xl p-5">
                <div className="flex items-center justify-between">
                  <div className="flex h-11 w-11 items-center justify-center rounded-xl bg-pharma-mint text-pharma-teal">
                    <Icon aria-hidden="true" size={21} />
                  </div>
                  <span className="rounded-full bg-emerald-50 px-2.5 py-1 text-xs font-semibold text-pharma-teal">
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
          <article className="pg-card rounded-2xl p-6">
            <div className="mb-4 flex items-center gap-3">
              <div className="flex h-11 w-11 items-center justify-center rounded-xl bg-pharma-mint text-pharma-teal">
                <ShieldCheck aria-hidden="true" size={21} />
              </div>
              <div>
                <p className="text-xs font-semibold uppercase text-pharma-teal">
                  Governance matrix
                </p>
                <h2 className="text-xl font-semibold">Safety & Evidence Status</h2>
                <p className="text-sm text-pharma-muted">Prototype boundaries</p>
              </div>
            </div>
            <div className="divide-y divide-pharma-line overflow-hidden rounded-2xl border border-pharma-line bg-white">
              {governanceRows.map(([label, value]) => (
                <div key={label} className="grid gap-2 p-3 sm:grid-cols-[230px_1fr]">
                  <p className="text-sm font-semibold text-pharma-ink">{label}</p>
                  <p className="text-sm leading-6 text-pharma-muted">{value}</p>
                </div>
              ))}
            </div>
          </article>

          <aside className="pg-card rounded-2xl p-6">
            <div className="mb-4 flex items-center gap-3">
              <div className="flex h-11 w-11 items-center justify-center rounded-xl bg-amber-50 text-amber-700">
                <AlertTriangle aria-hidden="true" size={21} />
              </div>
              <div>
                <p className="text-xs font-semibold uppercase text-pharma-teal">
                  Demo controls
                </p>
                <h2 className="text-xl font-semibold">Readiness Checklist</h2>
              </div>
            </div>
            <ul className="space-y-3 text-sm leading-6 text-pharma-muted">
              {readinessItems.map((item) => (
                <li key={item} className="flex gap-2">
                  <CheckCircle2 aria-hidden="true" className="mt-1 shrink-0 text-pharma-teal" size={16} />
                  <span>{item}</span>
                </li>
              ))}
            </ul>
            <div className="mt-5 rounded-xl border border-amber-200 bg-amber-50 p-3 text-sm leading-6 text-amber-900">
              Evidence is synthetic engineering proof only. It is not a substitute for
              pharmacist judgment, validation, or approved clinical sources.
            </div>
          </aside>
        </section>
      </div>
    </main>
  );
}
