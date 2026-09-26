import type { LucideIcon } from "lucide-react";
import { Activity, BarChart3, Goal, Target, TrendingUp } from "lucide-react";
import { cn } from "@/lib/utils";

export interface StatCardItem {
  label: string;
  value: string | number | null | undefined;
  hint?: string;
  icon?: LucideIcon;
  tone?: "brand" | "info" | "success" | "warn" | "danger" | "violet";
}

const TONE_CLASS = {
  brand: "bg-brand/15 text-brand",
  info: "bg-info/15 text-info",
  success: "bg-success/15 text-success",
  warn: "bg-warn/15 text-warn",
  danger: "bg-danger/15 text-danger",
  violet: "bg-violet/15 text-violet",
} as const;

const DEFAULT_ICONS = [Target, TrendingUp, Goal, BarChart3, Activity];

/** Ana səhifənin üst hissəsindəki statistik kartlar. */
export function StatCards({ items }: { items: StatCardItem[] }) {
  if (items.length === 0) return null;

  return (
    <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-4">
      {items.map((item, i) => {
        const Icon = item.icon ?? DEFAULT_ICONS[i % DEFAULT_ICONS.length];
        const tone = item.tone ?? "brand";
        return (
          <div key={item.label} className="card flex items-center gap-3 p-3.5">
            <span
              className={cn(
                "grid h-10 w-10 shrink-0 place-items-center rounded-lg",
                TONE_CLASS[tone],
              )}
            >
              <Icon className="h-5 w-5" />
            </span>
            <div className="min-w-0">
              <p className="truncate text-xs text-ink-faint">{item.label}</p>
              <p className="text-lg font-bold tabular-nums text-ink">
                {item.value ?? "—"}
              </p>
              {item.hint && (
                <p className="truncate text-[11px] text-ink-muted">{item.hint}</p>
              )}
            </div>
          </div>
        );
      })}
    </div>
  );
}
