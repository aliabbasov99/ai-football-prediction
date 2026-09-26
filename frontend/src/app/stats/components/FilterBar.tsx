"use client";

import { motion, useReducedMotion } from "framer-motion";
import { Search, X } from "lucide-react";

/** Cədvəl sətirləri arasında söz axtarışı — parent filtrasiyanı idarə edir. */
export function FilterBar({
  value,
  onChange,
  placeholder = "Komanda və ya AÇLAMA axtarın…",
}: {
  value: string;
  onChange: (value: string) => void;
  placeholder?: string;
}) {
  const reduce = useReducedMotion();

  return (
    <div className="relative flex-1">
      <Search
        className="pointer-events-none absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-ink-faint"
        strokeWidth={2.25}
      />
      <input
        value={value}
        onChange={(e) => onChange(e.target.value)}
        placeholder={placeholder}
        className="input !pl-9 !pr-9"
      />
      {value && (
        <motion.button
          onClick={() => onChange("")}
          initial={reduce ? false : { opacity: 0, scale: 0.8 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ duration: 0.14, ease: "easeOut" }}
          className="absolute right-2 top-1/2 grid h-6 w-6 -translate-y-1/2 place-items-center rounded-md text-ink-faint transition-colors duration-150 hover:bg-surface-2 hover:text-ink"
          aria-label="Təmizlət"
        >
          <X className="h-3.5 w-3.5" strokeWidth={2.5} />
        </motion.button>
      )}
    </div>
  );
}
