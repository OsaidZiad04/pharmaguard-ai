import {
  ClipboardPenLine,
  FileSearch,
  MessageSquareText,
  ShieldAlert,
  UserCheck
} from "lucide-react";

const steps = [
  {
    label: "Intake",
    detail: "OCR or text",
    status: "Active",
    icon: ClipboardPenLine,
    tone: "teal"
  },
  {
    label: "Extract",
    detail: "Medication terms",
    status: "Waiting",
    icon: FileSearch,
    tone: "slate"
  },
  {
    label: "Safety",
    detail: "Rules and context",
    status: "Review",
    icon: ShieldAlert,
    tone: "amber"
  },
  {
    label: "Review",
    detail: "Pharmacist gate",
    status: "Required",
    icon: UserCheck,
    tone: "amber"
  },
  {
    label: "Counseling",
    detail: "Draft support",
    status: "Gated",
    icon: MessageSquareText,
    tone: "slate"
  }
] as const;

const toneClasses = {
  teal: {
    icon: "border-emerald-200 bg-pharma-mint text-pharma-teal",
    badge: "bg-emerald-50 text-pharma-teal"
  },
  amber: {
    icon: "border-amber-200 bg-amber-50 text-amber-700",
    badge: "bg-amber-50 text-amber-800"
  },
  slate: {
    icon: "border-slate-200 bg-slate-50 text-slate-600",
    badge: "bg-slate-50 text-slate-600"
  }
};

export function WorkflowStepper() {
  return (
    <section className="pg-card rounded-2xl p-4 sm:p-5">
      <div className="mb-4 flex flex-col gap-1 sm:flex-row sm:items-end sm:justify-between">
        <div>
          <p className="text-xs font-semibold uppercase text-pharma-teal">
            AI-assisted workflow
          </p>
          <h2 className="text-lg font-semibold text-pharma-ink">Prescription Pipeline</h2>
        </div>
        <p className="max-w-2xl text-sm leading-6 text-pharma-muted">
          Intake can start with text or OCR, but pharmacist review remains the control point.
        </p>
      </div>

      <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-5">
        {steps.map((step, index) => {
          const Icon = step.icon;
          const tone = toneClasses[step.tone];
          return (
            <article
              key={step.label}
              className="rounded-xl border border-pharma-line bg-white p-3 shadow-sm"
            >
              <div className="flex items-center gap-3">
                <div
                  className={`flex h-10 w-10 shrink-0 items-center justify-center rounded-xl border ${tone.icon}`}
                >
                  <Icon aria-hidden="true" size={18} />
                </div>
                <div className="min-w-0">
                  <div className="flex flex-wrap items-center gap-2">
                    <p className="text-xs font-medium uppercase text-pharma-muted">
                      Step {index + 1}
                    </p>
                    <span
                      className={`rounded-full px-2 py-0.5 text-[11px] font-semibold ${tone.badge}`}
                    >
                      {step.status}
                    </span>
                  </div>
                  <p className="mt-1 text-sm font-semibold text-pharma-ink">{step.label}</p>
                  <p className="text-xs leading-5 text-pharma-muted">{step.detail}</p>
                </div>
              </div>
            </article>
          );
        })}
      </div>
    </section>
  );
}
