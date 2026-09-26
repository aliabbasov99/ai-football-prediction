import { cn } from "@/lib/utils";

interface ProgressBarProps {
  value: number;
  status?: string;
}

export function ProgressBar({ value, status }: ProgressBarProps) {
  const pct = Math.max(0, Math.min(100, value));

  return (
    <div className="space-y-1.5">
      <div className="h-2 w-full overflow-hidden rounded-full bg-surface-3">
        <div
          className={cn(
            "h-full rounded-full transition-all duration-300",
            status === "error" ? "bg-danger" : "bg-brand",
          )}
          style={{ width: `${pct}%` }}
        />
      </div>
      {status && (
        <p className="text-xs text-ink-faint">
          {status} · {pct.toFixed(0)}%
        </p>
      )}
    </div>
  );
}
