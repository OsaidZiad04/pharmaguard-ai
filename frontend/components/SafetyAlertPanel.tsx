import { AlertTriangle, Info, ShieldAlert } from "lucide-react";

import type { SafetyAlert } from "@/lib/types";

interface SafetyAlertPanelProps {
  alerts: SafetyAlert[];
}

export function SafetyAlertPanel({ alerts }: SafetyAlertPanelProps) {
  return (
    <section className="rounded-lg border border-pharma-line bg-white p-5 shadow-panel">
      <div className="mb-4 flex items-center gap-3">
        <div className="flex h-9 w-9 items-center justify-center rounded-md bg-amber-50 text-pharma-amber">
          <ShieldAlert aria-hidden="true" size={18} />
        </div>
        <div>
          <h2 className="text-lg font-semibold text-pharma-ink">Safety Alerts</h2>
          <p className="text-sm text-pharma-muted">Guardrail status</p>
        </div>
      </div>

      {alerts.length > 0 ? (
        <div className="space-y-3">
          {alerts.map((alert) => (
            <div key={`${alert.code}-${alert.message}`} className={alertClassName(alert.severity)}>
              {alert.severity === "info" ? (
                <Info aria-hidden="true" size={18} />
              ) : (
                <AlertTriangle aria-hidden="true" size={18} />
              )}
              <div>
                <p className="text-sm font-semibold">{formatCode(alert.code)}</p>
                <p className="mt-1 text-sm">{alert.message}</p>
              </div>
            </div>
          ))}
        </div>
      ) : (
        <div className="rounded-md border border-dashed border-pharma-line p-4 text-sm text-pharma-muted">
          Alerts appear after review activity.
        </div>
      )}
    </section>
  );
}

function alertClassName(severity: SafetyAlert["severity"]) {
  const base = "flex gap-3 rounded-md border p-3";
  if (severity === "critical") {
    return `${base} border-red-200 bg-red-50 text-red-800`;
  }
  if (severity === "warning") {
    return `${base} border-amber-200 bg-amber-50 text-amber-800`;
  }
  return `${base} border-emerald-200 bg-emerald-50 text-pharma-teal`;
}

function formatCode(code: string) {
  return code
    .split("_")
    .map((part) => part.charAt(0) + part.slice(1).toLowerCase())
    .join(" ");
}
