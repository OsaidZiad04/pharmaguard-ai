import Link from "next/link";
import { FileText, FlaskConical, Languages, ShieldCheck } from "lucide-react";
import type { LucideIcon } from "lucide-react";

export function AppHeader() {
  return (
    <header className="sticky top-0 z-30 border-b border-white/70 bg-white/88 shadow-sm backdrop-blur-xl">
      <div className="mx-auto flex max-w-7xl flex-col gap-3 px-4 py-3 sm:px-6 lg:flex-row lg:items-center lg:justify-between lg:px-8">
        <div className="flex min-w-0 items-center gap-3">
          <div className="flex h-12 w-12 shrink-0 items-center justify-center overflow-hidden rounded-xl border border-emerald-100 bg-pharma-slate shadow-glow">
            <img
              src="/brand/pharmaguard-logo-icon.png"
              alt=""
              className="h-full w-full object-cover"
            />
          </div>
          <div className="min-w-0">
            <div className="flex flex-wrap items-center gap-x-3 gap-y-1">
              <h1 className="text-xl font-semibold text-pharma-ink sm:text-2xl">
                PharmaGuard AI
              </h1>
              <span className="rounded-full border border-emerald-200 bg-emerald-50 px-2.5 py-1 text-xs font-semibold text-pharma-teal">
                Prototype
              </span>
            </div>
            <p className="text-sm leading-5 text-pharma-muted">
              Smart Prescription Intelligence for Pharmacists
            </p>
          </div>
        </div>

        <div className="flex max-w-full flex-wrap items-center justify-start gap-2 lg:justify-end">
          <TrustBadge icon={ShieldCheck} label="Pharmacist review required" tone="teal" />
          <TrustBadge icon={FileText} label="Draft support only" tone="slate" />
          <TrustBadge icon={FlaskConical} label="Synthetic data only" tone="amber" />
          <Link
            href="/evaluation"
            className="inline-flex h-9 items-center rounded-full border border-pharma-line bg-white px-3 text-sm font-semibold text-pharma-ink transition hover:border-pharma-teal hover:text-pharma-teal"
          >
            View evidence
          </Link>
          {/* Future RTL: wire this placeholder to locale and dir state when Arabic copy is introduced. */}
          <div
            aria-disabled="true"
            aria-label="Language toggle placeholder. Arabic support planned."
            title="Arabic support planned"
            className="inline-flex h-9 cursor-not-allowed items-center gap-1 rounded-full border border-pharma-line bg-white p-1 text-xs font-semibold text-pharma-muted opacity-90"
          >
            <Languages aria-hidden="true" size={14} />
            <span className="rounded-full bg-pharma-slate px-2 py-1 text-white">EN</span>
            <span className="px-2 py-1">AR soon</span>
          </div>
        </div>
      </div>
    </header>
  );
}

function TrustBadge({
  icon: Icon,
  label,
  tone
}: {
  icon: LucideIcon;
  label: string;
  tone: "teal" | "slate" | "amber";
}) {
  const toneClass =
    tone === "teal"
      ? "border-emerald-200 bg-emerald-50 text-pharma-teal"
      : tone === "amber"
        ? "border-amber-200 bg-amber-50 text-amber-800"
        : "border-slate-200 bg-slate-50 text-slate-700";

  return (
    <span
      className={`inline-flex min-h-9 items-center gap-2 rounded-full border px-3 py-1 text-xs font-semibold sm:text-sm ${toneClass}`}
    >
      <Icon aria-hidden="true" size={15} />
      {label}
    </span>
  );
}
