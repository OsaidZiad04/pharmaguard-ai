import { ClipboardPenLine, FileSearch, ShieldAlert, UserCheck, MessageSquareText } from "lucide-react";

const steps = [
  { label: "Intake", icon: ClipboardPenLine },
  { label: "Extract", icon: FileSearch },
  { label: "Safety", icon: ShieldAlert },
  { label: "Review", icon: UserCheck },
  { label: "Counseling", icon: MessageSquareText }
];

export function WorkflowStepper() {
  return (
    <section className="rounded-lg border border-pharma-line bg-white p-4 shadow-panel">
      <div className="grid grid-cols-2 gap-3 sm:grid-cols-5">
        {steps.map((step, index) => {
          const Icon = step.icon;
          return (
            <div key={step.label} className="flex items-center gap-3">
              <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-md border border-emerald-200 bg-pharma-mint text-pharma-teal">
                <Icon aria-hidden="true" size={18} />
              </div>
              <div>
                <p className="text-xs font-medium uppercase text-pharma-muted">Step {index + 1}</p>
                <p className="text-sm font-semibold text-pharma-ink">{step.label}</p>
              </div>
            </div>
          );
        })}
      </div>
    </section>
  );
}
