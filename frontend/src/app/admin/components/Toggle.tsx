"use client";

import { motion, useReducedMotion } from "framer-motion";
import { cn } from "@/lib/utils";

interface ToggleProps {
  label: string;
  checked: boolean;
  onChange: (checked: boolean) => void;
  disabled?: boolean;
  hint?: string;
}

export function Toggle({ label, checked, onChange, disabled, hint }: ToggleProps) {
  const reduce = useReducedMotion();

  return (
    <label
      className={cn(
        "flex items-center gap-2.5 rounded-lg border px-3 py-2.5 transition-colors duration-150",
        checked
          ? "border-brand/30 bg-brand/[0.06]"
          : "border-line-soft bg-surface/40",
        disabled ? "cursor-not-allowed opacity-50" : "cursor-pointer hover:border-line",
      )}
    >
      <input
        type="checkbox"
        checked={checked}
        disabled={disabled}
        onChange={(e) => onChange(e.target.checked)}
        className="sr-only"
      />

      <span
        className={cn(
          "relative h-5 w-9 shrink-0 rounded-full transition-colors duration-200",
          checked ? "bg-brand" : "bg-surface-3",
        )}
      >
        <motion.span
          animate={reduce ? undefined : { x: checked ? 18 : 2 }}
          transition={{ duration: 0.18, ease: [0.22, 1, 0.36, 1] }}
          className="absolute top-0.5 h-4 w-4 rounded-full bg-ink shadow-none"
        />
      </span>

      <span className="min-w-0 flex-1">
        <span
          className={cn(
            "block text-sm font-medium",
            checked ? "text-ink" : "text-ink-muted",
          )}
        >
          {label}
        </span>
        {hint && <span className="block text-[11px] text-ink-faint">{hint}</span>}
      </span>
    </label>
  );
}
