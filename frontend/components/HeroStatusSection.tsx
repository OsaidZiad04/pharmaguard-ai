import Link from "next/link";
import {
  BookOpenCheck,
  DatabaseZap,
  FlaskConical,
  LockKeyhole,
  ShieldCheck,
  UserCheck
} from "lucide-react";

const statusCards = [
  {
    label: "OCR correction gated",
    detail: "Unverified OCR cannot move downstream.",
    icon: LockKeyhole,
    tone: "amber"
  },
  {
    label: "RAG grounded",
    detail: "Local Markdown sources are surfaced.",
    icon: BookOpenCheck,
    tone: "teal"
  },
  {
    label: "KB governance enabled",
    detail: "Review status remains visible.",
    icon: DatabaseZap,
    tone: "slate"
  },
  {
    label: "Safety rules active",
    detail: "Findings remain pharmacist-review prompts.",
    icon: ShieldCheck,
    tone: "teal"
  },
  {
    label: "Pharmacist review required",
    detail: "Patient-facing final advice is disabled.",
    icon: UserCheck,
    tone: "amber"
  }
] as const;

export function HeroStatusSection() {
  return (
    <section className="relative overflow-hidden rounded-2xl border border-white/80 bg-white shadow-command">
      <div className="pg-hero-grid absolute inset-0 opacity-70" aria-hidden="true" />
      <div className="relative grid gap-6 p-5 sm:p-6 lg:grid-cols-[minmax(0,0.95fr)_minmax(360px,1.05fr)] lg:p-8">
        <div className="flex flex-col justify-between gap-6">
          <div>
            <div className="mb-5 inline-flex max-w-full items-center gap-3 rounded-2xl border border-pharma-line bg-white/95 px-3 py-2 shadow-sm">
              <img
                src="/brand/pharmaguard-logo-main.png"
                alt="PharmaGuard AI"
                className="h-12 max-w-56 object-contain sm:h-14 sm:max-w-72"
              />
            </div>
            <p className="text-sm font-semibold uppercase text-pharma-teal">
              AI pharmacist command center
            </p>
            <h2 className="mt-3 max-w-3xl text-3xl font-semibold leading-tight text-pharma-ink sm:text-4xl lg:text-5xl">
              Safety-first prescription intelligence with pharmacist control.
            </h2>
            <p className="mt-4 max-w-2xl text-base leading-7 text-pharma-muted">
              PharmaGuard AI demonstrates OCR intake, correction-gated analysis,
              source-grounded local RAG, KB governance, retrieval diagnostics,
              and deterministic safety prompts for pharmacist review.
            </p>
            <div className="mt-5 flex flex-wrap gap-2 text-xs font-semibold">
              <span className="rounded-full border border-amber-200 bg-amber-50 px-3 py-1.5 text-amber-900">
                Prototype only
              </span>
              <span className="rounded-full border border-slate-200 bg-slate-50 px-3 py-1.5 text-slate-700">
                Not clinically validated
              </span>
              <span className="rounded-full border border-emerald-200 bg-emerald-50 px-3 py-1.5 text-pharma-teal">
                Pharmacist-in-the-loop
              </span>
            </div>
          </div>

          <div className="flex flex-col gap-3 sm:flex-row sm:items-center">
            <Link
              href="/evaluation"
              className="inline-flex items-center justify-center gap-2 rounded-xl bg-pharma-slate px-4 py-3 text-sm font-semibold text-white shadow-sm transition hover:bg-slate-800"
            >
              <FlaskConical aria-hidden="true" size={17} />
              View evaluation evidence
            </Link>
            <p className="text-sm leading-6 text-pharma-muted">
              Synthetic data only. Draft support only. No autonomous medical decisions.
            </p>
          </div>
        </div>

        <div className="grid gap-4">
          <div className="overflow-hidden rounded-2xl border border-slate-800/20 bg-pharma-slate p-2 shadow-glow">
            <img
              src="/brand/pharmaguard-hero-visual.png"
              alt="PharmaGuard AI prescription review command center visual"
              className="aspect-[16/9] w-full rounded-xl object-cover"
            />
          </div>

          <div className="grid gap-3 sm:grid-cols-2 xl:grid-cols-5">
            {statusCards.map((card) => {
              const Icon = card.icon;
              return (
                <article
                  key={card.label}
                  className="rounded-xl border border-pharma-line bg-white/92 p-3 shadow-sm"
                >
                  <div className={statusIconClassName(card.tone)}>
                    <Icon aria-hidden="true" size={17} />
                  </div>
                  <h3 className="mt-3 text-sm font-semibold leading-5 text-pharma-ink">
                    {card.label}
                  </h3>
                  <p className="mt-1 text-xs leading-5 text-pharma-muted">{card.detail}</p>
                </article>
              );
            })}
          </div>
        </div>
      </div>
    </section>
  );
}

function statusIconClassName(tone: "teal" | "amber" | "slate") {
  const base = "flex h-9 w-9 items-center justify-center rounded-lg";
  if (tone === "amber") {
    return `${base} bg-amber-50 text-amber-700`;
  }
  if (tone === "slate") {
    return `${base} bg-slate-100 text-pharma-slate`;
  }
  return `${base} bg-pharma-mint text-pharma-teal`;
}
