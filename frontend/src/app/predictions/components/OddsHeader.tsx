"use client";

import { MARKET_OPTIONS, type MarketKey } from "./types";
import { cn } from "@/lib/utils";

interface OddsHeaderProps {
  active: Set<string>;
  onToggle: (key: string) => void;
}

/** Sütun başlıqları — hansı bazaların görünəcəyini idarə edir. */
export function OddsHeader({ active, onToggle }: OddsHeaderProps) {
  return (
    <div className="flex flex-wrap items-center gap-1.5">
      <span className="mr-1 text-[10px] font-semibold uppercase tracking-wide text-ink-faint">
        Bazarlar
      </span>
      {MARKET_OPTIONS.map((col: { key: MarketKey; label: string }) => {
        const on = active.has(col.key);
        return (
          <button
            key={col.key}
            onClick={() => onToggle(col.key)}
            aria-pressed={on}
            className={cn(
              "rounded-md px-2 py-1 text-[11px] font-medium transition-colors",
              on
                ? "bg-surface-3 text-ink"
                : "bg-surface-2 text-ink-faint hover:text-ink-muted",
            )}
          >
            {col.label}
          </button>
        );
      })}
    </div>
  );
}
