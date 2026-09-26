"use client";

import { cn } from "@/lib/utils";

interface ToggleProps {
  label: string;
  checked: boolean;
  onChange: (checked: boolean) => void;
  disabled?: boolean;
  hint?: string;
}

export function Toggle({ label, checked, onChange, disabled, hint }: ToggleProps) {
  return (
    <label
      className={cn(
        "flex items-center gap-2.5 rounded-lg border border-line-soft bg-surface-2 px-3 py-2 transition-colors",
        disabled ? "opacity-50" : "cursor-pointer hover:bg-surface-3",
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
          "relative h-5 w-9 shrink-0 rounded-full transition-colors",
          checked ? "bg-brand" : "bg-surface-3",
        )}
      >
        <span
          className={cn(
            "absolute top-0.5 h-4 w-4 rounded-full bg-white transition-transform",
            checked ? "translate-x-4.5" : "translate-x-0.5",
          )}
        />
      </span>
      <span className="min-w-0 flex-1">
        <span className="block text-sm font-medium text-ink">{label}</span>
        {hint && <span className="block text-[11px] text-ink-faint">{hint}</span>}
      </span>
    </label>
  );
}
