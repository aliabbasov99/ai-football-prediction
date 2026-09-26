"use client";

import { motion, useReducedMotion } from "framer-motion";
import { MARKET_OPTIONS, type MarketKey } from "./types";
import { cn } from "@/lib/utils";

interface OddsHeaderProps {
  active: Set<string>;
  onToggle: (key: string) => void;
}

/** Sütun başlıqları — hansı bazaların göstəriləcəyini idarə edir. */
export function OddsHeader({ active, onToggle }: OddsHeaderProps) {
  const reduce = useReducedMotion();

  return (
    <div className="flex flex-wrap items-center gap-1.5">
      <span className="mr-1 text-[10px] font-semibold uppercase tracking-wider text-ink-faint">
        Bazarlar
      </span>
      {MARKET_OPTIONS.map((col: { key: MarketKey; label: string }) => {
        const on = active.has(col.key);
        return (
          <motion.button
            key={col.key}
            onClick={() => onToggle(col.key)}
            aria-pressed={on}
            whileTap={reduce ? undefined : { scale: 0.95 }}
            transition={{ duration: 0.1, ease: "easeOut" }}
            className={cn(
              "rounded-md border px-2.5 py-1.5 text-[11px] font-medium transition-colors duration-150",
              on
                ? "border-brand/30 bg-brand/10 text-brand"
                : "border-transparent text-ink-faint hover:bg-surface-2 hover:text-ink-muted",
            )}
          >
            {col.label}
          </motion.button>
        );
      })}
    </div>
  );
}
