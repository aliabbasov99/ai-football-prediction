"use client";

import { extractNumber } from "./constants";
import { PercentBar } from "./PercentBar";
import type { BarTone } from "./types";

/**
 * Statistika səhifələri üçün kiçik yardımçı komponentlər.
 * (structure.md: src/app/stats/components/utils.tsx)
 */

/** Faiz dəyərini 0-100 aralığına sığdırır. */
export function clampPercent(value: number): number {
  return Math.max(0, Math.min(100, value));
}

/** Sətir daxilində maksimum reqem sütununu tapır ("Score", "%", "rate" və s.). */
export function maxColumnValues(
  headers: string[],
  rows: (string | null)[][],
): Map<number, number> {
  const result = new Map<number, number>();
  headers.forEach((header, colIndex) => {
    if (!/score|rate|pct|%|\/ ?game/i.test(header)) return;
    let max = 0;
    for (const row of rows) {
      const n = extractNumber(row[colIndex]);
      if (n !== null && n > max) max = n;
    }
    result.set(colIndex, max);
  });
  return result;
}

/** Dəyər faizdir? (30, "46%", "0.46%") */
export function isPercentValue(value: string | null | undefined): boolean {
  return typeof value === "string" && value.includes("%");
}

/** Sadə faiz göstəricisi — komanda adının yanında. */
export function InlinePercent({
  value,
  tone,
}: {
  value: string | number | null | undefined;
  tone?: BarTone;
}) {
  const n = extractNumber(value);
  if (n === null) return <span className="text-ink-faint">—</span>;
  return (
    <span className="flex items-center gap-2">
      <span className="w-10 shrink-0 text-right text-xs tabular-nums text-ink-muted">
        {n.toFixed(0)}%
      </span>
      <span className="w-16">
        <PercentBar value={n} tone={tone ?? (n >= 50 ? "success" : "info")} />
      </span>
    </span>
  );
}
