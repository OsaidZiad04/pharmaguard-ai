import { ClipboardList, ShieldCheck } from "lucide-react";

export function AppHeader() {
  return (
    <header className="border-b border-pharma-line bg-white">
      <div className="mx-auto flex max-w-7xl flex-col gap-4 px-5 py-5 sm:px-6 lg:flex-row lg:items-center lg:justify-between lg:px-8">
        <div className="flex items-center gap-3">
          <div className="flex h-11 w-11 items-center justify-center rounded-md bg-pharma-mint text-pharma-teal">
            <ClipboardList aria-hidden="true" size={24} />
          </div>
          <div>
            <h1 className="text-2xl font-semibold text-pharma-ink">PharmaGuard AI</h1>
            <p className="text-sm text-pharma-muted">Smart Prescription Desk for Pharmacists</p>
          </div>
        </div>
        <div className="flex items-center gap-2 rounded-md border border-emerald-200 bg-emerald-50 px-3 py-2 text-sm font-medium text-pharma-teal">
          <ShieldCheck aria-hidden="true" size={18} />
          <span>Pharmacist review required</span>
        </div>
      </div>
    </header>
  );
}
