import { AlertCircle, CheckCircle2 } from "lucide-react";
import type { PipelineState } from "@/types/football";

/** Pipeline yekun hesabatı — hansı mənbədə neçə fixture var. */
export function PipelineReport({ report }: { report: Record<string, unknown> | null }) {
  if (!report || Object.keys(report).length === 0) return null;

  return (
    <div className="card overflow-hidden">
      <div className="border-b border-line bg-surface-2 px-3 py-2.5">
        <h3 className="text-sm font-bold text-ink">Yekun hesabat</h3>
      </div>
      <ul className="divide-y divide-line-soft">
        {Object.entries(report).map(([key, value]) => (
          <li key={key} className="flex items-center justify-between gap-3 px-3 py-2 text-sm">
            <span className="flex items-center gap-2 text-ink-muted">
              {typeof value === "number" && value > 0 ? (
                <CheckCircle2 className="h-3.5 w-3.5 text-success" />
              ) : (
                <AlertCircle className="h-3.5 w-3.5 text-ink-faint" />
              )}
              {key.replace(/_/g, " ")}
            </span>
            <span className="font-bold tabular-nums text-ink">
              {typeof value === "number" ? value : String(value)}
            </span>
          </li>
        ))}
      </ul>
    </div>
  );
}

export function PipelineStatusCard({ state }: { state: PipelineState | null }) {
  if (!state) return null;

  return (
    <div className="card p-3.5">
      <div className="flex items-center justify-between">
        <span className="text-sm font-semibold text-ink">Vəziyyət</span>
        <span
          className={
            state.is_running
              ? "rounded-md bg-warn/15 px-2 py-0.5 text-xs font-bold text-warn"
              : "rounded-md bg-surface-3 px-2 py-0.5 text-xs font-bold text-ink-faint"
          }
        >
          {state.is_running ? "İşləyir" : "Dayanıb"}
        </span>
      </div>

      <dl className="mt-3 grid grid-cols-2 gap-2 text-xs">
        <div>
          <dt className="text-ink-faint">Cari addım</dt>
          <dd className="font-semibold text-ink">
            {state.current_step || "—"}
            {state.total_steps > 0 && (
              <span className="ml-1 text-ink-faint">
                ({state.current_step_index + 1}/{state.total_steps})
              </span>
            )}
          </dd>
        </div>
        <div>
          <dt className="text-ink-faint">Status</dt>
          <dd className="font-semibold text-ink">{state.step_status || "—"}</dd>
        </div>
      </dl>

      {state.error && (
        <p className="mt-3 rounded-lg border border-danger/30 bg-danger/10 p-2 text-xs text-danger">
          {state.error}
        </p>
      )}
    </div>
  );
}
