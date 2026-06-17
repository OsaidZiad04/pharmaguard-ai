import {
  BookOpenCheck,
  CheckCircle2,
  Circle,
  FileText,
  LockKeyhole,
  PencilLine,
  SearchCheck,
  ShieldCheck
} from "lucide-react";

export type WorkflowStepStatus = "waiting" | "required" | "ready" | "completed" | "blocked";

export interface WorkflowStatusStep {
  label: string;
  status: WorkflowStepStatus;
  summary: string;
}

interface WorkflowStatusPanelProps {
  steps: WorkflowStatusStep[];
}

const iconByLabel = {
  "OCR Intake": FileText,
  "Pharmacist Correction": PencilLine,
  "Prescription Analysis": SearchCheck,
  "Medication Extraction": CheckCircle2,
  "RAG Source Check": BookOpenCheck,
  "Counseling Draft": FileText,
  "Pharmacist Review": ShieldCheck
};

export function WorkflowStatusPanel({ steps }: WorkflowStatusPanelProps) {
  return (
    <section className="pg-card rounded-2xl p-5">
      <div className="mb-4 flex flex-col gap-1 sm:flex-row sm:items-end sm:justify-between">
        <div>
          <p className="text-xs font-semibold uppercase text-pharma-teal">
            Live workflow trace
          </p>
          <h2 className="text-lg font-semibold text-pharma-ink">Workflow Status</h2>
          <p className="text-sm text-pharma-muted">
            Correction boundary, source grounding, and review state
          </p>
        </div>
        <span className="inline-flex w-fit items-center gap-1 rounded-md border border-amber-200 bg-amber-50 px-2.5 py-1 text-xs font-semibold text-amber-900">
          <LockKeyhole aria-hidden="true" size={13} />
          Unverified OCR blocked
        </span>
      </div>

      <ol className="grid gap-3 md:grid-cols-2 xl:grid-cols-7">
        {steps.map((step, index) => {
          const Icon = iconByLabel[step.label as keyof typeof iconByLabel] ?? Circle;
          return (
            <li key={step.label} className="relative">
              {index < steps.length - 1 ? (
                <div className="absolute left-5 top-10 hidden h-px w-[calc(100%-1.25rem)] bg-pharma-line xl:block" />
              ) : null}
              <div className="relative h-full rounded-xl border border-pharma-line bg-white p-3 shadow-sm">
                <div className="mb-3 flex items-center justify-between gap-2">
                  <span className={statusIconClassName(step.status)}>
                    <Icon aria-hidden="true" size={16} />
                  </span>
                  <span className={statusBadgeClassName(step.status)}>
                    {formatStatus(step.status)}
                  </span>
                </div>
                <p className="text-sm font-semibold text-pharma-ink">{step.label}</p>
                <p className="mt-1 text-xs leading-5 text-pharma-muted">{step.summary}</p>
              </div>
            </li>
          );
        })}
      </ol>
    </section>
  );
}

function statusIconClassName(status: WorkflowStepStatus) {
  const base = "inline-flex h-9 w-9 items-center justify-center rounded-xl";
  if (status === "completed") {
    return `${base} bg-emerald-100 text-pharma-teal`;
  }
  if (status === "ready") {
    return `${base} bg-cyan-50 text-cyan-700`;
  }
  if (status === "required") {
    return `${base} bg-amber-50 text-amber-700`;
  }
  if (status === "blocked") {
    return `${base} bg-red-50 text-red-700`;
  }
  return `${base} bg-white text-pharma-muted`;
}

function statusBadgeClassName(status: WorkflowStepStatus) {
  const base = "rounded-full px-2 py-1 text-[11px] font-semibold uppercase";
  if (status === "completed") {
    return `${base} bg-emerald-100 text-pharma-teal`;
  }
  if (status === "ready") {
    return `${base} bg-cyan-50 text-cyan-700`;
  }
  if (status === "required") {
    return `${base} bg-amber-50 text-amber-800`;
  }
  if (status === "blocked") {
    return `${base} bg-red-50 text-red-700`;
  }
  return `${base} bg-white text-pharma-muted`;
}

function formatStatus(status: WorkflowStepStatus) {
  return status.charAt(0).toUpperCase() + status.slice(1);
}
