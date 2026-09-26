"use client";

import { Search, X } from "lucide-react";

/** Cədvəl sətirləri arasında söz axtarışı — parent filtrasiyanı idarə edir. */
export function FilterBar({
  value,
  onChange,
  placeholder = "Komanda və ya ölçü axtarın…",
}: {
  value: string;
  onChange: (value: string) => void;
  placeholder?: string;
}) {
  return (
    <div className="relative">
      <Search className="pointer-events-none absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-ink-faint" />
      <input
        value={value}
        onChange={(e) => onChange(e.target.value)}
        placeholder={placeholder}
        className="w-full rounded-lg border border-line bg-surface py-2 pl-9 pr-9 text-sm text-ink outline-none placeholder:text-ink-faint focus:border-brand"
      />
      {value && (
        <button
          onClick={() => onChange("")}
          className="absolute right-2 top-1/2 grid h-6 w-6 -translate-y-1/2 place-items-center rounded-md text-ink-faint hover:bg-surface-2 hover:text-ink"
          aria-label="Təmizlə"
        >
          <X className="h-3.5 w-3.5" />
        </button>
      )}
    </div>
  );
}
