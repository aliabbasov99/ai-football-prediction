"use client";

import { motion, useReducedMotion } from "framer-motion";
import { Check } from "lucide-react";
import { cn } from "@/lib/utils";

interface ProgressBarProps {
  value: number;
  status?: string;
}

/** "idle" / "running" / … backend kodunu insan oxuyan mətnə çevirir. */
const STATUS_LABEL: Record<string, string> = {
  idle: "Gözləyir",
  running: "İşləyir",
  completed: "Tamamlandı",
  partial: "Problemlə bitdi",
  error: "Xəta",
};

export function ProgressBar({ value, status }: ProgressBarProps) {
  const reduce = useReducedMotion();
  const pct = Math.max(0, Math.min(100, value));
  const failed = status === "error";
  const partial = status === "partial";

  return (
    <div className="space-y-2">
      <div
        className="h-1.5 w-full overflow-hidden rounded-full bg-surface-3"
        role="progressbar"
        aria-valuenow={Math.round(pct)}
        aria-valuemin={0}
        aria-valuemax={100}
      >
        <motion.div
          initial={reduce ? false : { width: 0 }}
          animate={{ width: `${pct}%` }}
          transition={{ duration: 0.4, ease: [0.22, 1, 0.36, 1] }}
          className={cn(
            "h-full rounded-full",
            failed ? "bg-danger" : partial ? "bg-warn" : "bg-brand",
          )}
        />
      </div>
      {status && (
        <div className="flex items-center justify-between text-xs">
          <span
            className={cn(
              failed ? "text-danger" : partial ? "text-warn" : "text-ink-muted",
            )}
          >
            {STATUS_LABEL[status] ?? status}
          </span>
          <span className="font-medium tabular-nums text-ink">{pct.toFixed(0)}%</span>
        </div>
      )}
    </div>
  );
}

/** Kiçik tamamlanma işarəsi — hesabat bölmələrində. */
export function DoneMark() {
  return (
    <span className="grid h-4 w-4 place-items-center rounded-full bg-brand/15">
      <Check className="h-2.5 w-2.5 text-brand" strokeWidth={3} />
    </span>
  );
}
