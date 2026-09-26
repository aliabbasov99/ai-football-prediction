import type { LucideIcon } from "lucide-react";
import { Activity, Goal, Sigma, Target, TrendingUp, Users } from "lucide-react";
import { cn } from "@/lib/utils";
import { RevealItem, staggerList } from "@/components/motion";
import { motion, useReducedMotion } from "framer-motion";

export interface StatCardItem {
  label: string;
  value: string | number | null | undefined;
  hint?: string;
  icon?: LucideIcon;
  tone?: "brand" | "info" | "success" | "warn" | "danger";
}

const TONE_CLASS = {
  brand: "bg-brand/12 text-brand border-brand/20",
  info: "bg-surface-2 text-ink-muted border-line",
  success: "bg-success/12 text-success border-success/20",
  warn: "bg-warn/12 text-warn border-warn/20",
  danger: "bg-danger/12 text-danger border-danger/20",
} as const;

const DEFAULT_ICONS = [Target, Users, TrendingUp, Goal];

/** Ana səhifənin üst hissəsindəki statistik kartlar. */
export function StatCards({ items }: { items: StatCardItem[] }) {
  const reduce = useReducedMotion();
  if (items.length === 0) return null;

  return (
    <motion.div
      variants={reduce ? undefined : staggerList}
      initial={reduce ? false : "hidden"}
      animate="show"
      className="grid gap-3 sm:grid-cols-2 lg:grid-cols-4"
    >
      {items.map((item, i) => {
        const Icon = item.icon ?? DEFAULT_ICONS[i % DEFAULT_ICONS.length];
        const tone = item.tone ?? "brand";
        return (
          <RevealItem
            key={item.label}
            className="card card-hover flex items-center gap-3.5 p-4"
          >
            <span
              className={cn(
                "grid h-10 w-10 shrink-0 place-items-center rounded-lg border",
                TONE_CLASS[tone],
              )}
            >
              <Icon className="h-4.5 w-4.5" strokeWidth={2.25} />
            </span>
            <div className="min-w-0">
              <p className="truncate text-xs text-ink-faint">{item.label}</p>
              <p className="text-lg font-semibold tabular-nums text-ink">
                {item.value ?? "—"}
              </p>
              {item.hint && (
                <p className="truncate text-[11px] text-ink-muted">{item.hint}</p>
              )}
            </div>
          </RevealItem>
        );
      })}
    </motion.div>
  );
}

/**
 * Cədvəl sətirlərinin üstündəki seriya açarı (leqend).
 * Üç seriya üçün üç fərqli, amma zümrüd-dən başqa "krom" olmayan rəng:
 * vurğu (zümrüd) + neytral işıq + kəhrəba. Bənövşəvi/neon YOXDUR.
 */
export const SERIES_KEYS = [
  { label: "Son 30 oyun", swatch: "bg-brand" },
  { label: "Liqa", swatch: "bg-ink" },
  { label: "Kubok", swatch: "bg-warn" },
] as const;

export function SeriesLegend({ extra }: { extra?: string }) {
  const reduce = useReducedMotion();
  return (
    <div className="flex flex-wrap items-center gap-x-5 gap-y-1.5 text-xs text-ink-faint">
      {extra && <span className="font-medium text-ink">{extra}</span>}
      {SERIES_KEYS.map((s) => (
        <span key={s.label} className="flex items-center gap-1.5">
          <motion.span
            whileHover={reduce ? undefined : { scaleX: 1.6 }}
            transition={{ duration: 0.16, ease: "easeOut" }}
            className={cn("inline-block h-0.5 w-4 rounded-full", s.swatch)}
          />
          {s.label}
        </span>
      ))}
      <Sigma className="ml-1 h-3.5 w-3.5 text-ink-faint" strokeWidth={2.25} />
      <Activity className="h-3.5 w-3.5 text-ink-faint" strokeWidth={2.25} />
    </div>
  );
}
