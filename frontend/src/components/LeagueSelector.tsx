"use client";

import { AnimatePresence, motion, useReducedMotion } from "framer-motion";
import { ChevronDown, Trophy } from "lucide-react";
import { useEffect, useRef, useState } from "react";
import { TeamLogo } from "@/app/predictions/components/TeamLogo";
import { countryFlag } from "@/lib/countries";
import { LEAGUE_LOGO_FALLBACK } from "@/lib/logo";
import type { League } from "@/types/football";
import { cn } from "@/lib/utils";
import { DUR, EASE_OUT } from "@/components/motion";

interface LeagueSelectorProps {
  leagues: League[];
  value: string | null;
  onChange: (id: string) => void;
  label?: string;
}

export function LeagueSelector({ leagues, value, onChange, label }: LeagueSelectorProps) {
  const [open, setOpen] = useState(false);
  const ref = useRef<HTMLDivElement>(null);
  const reduce = useReducedMotion();

  useEffect(() => {
    if (!open) return;
    function onClick(e: MouseEvent) {
      if (ref.current && !ref.current.contains(e.target as Node)) setOpen(false);
    }
    function onKey(e: KeyboardEvent) {
      if (e.key === "Escape") setOpen(false);
    }
    document.addEventListener("mousedown", onClick);
    document.addEventListener("keydown", onKey);
    return () => {
      document.removeEventListener("mousedown", onClick);
      document.removeEventListener("keydown", onKey);
    };
  }, [open]);

  const selected = leagues.find((l) => l.id === value);

  return (
    <div ref={ref} className="relative">
      <motion.button
        onClick={() => setOpen((v) => !v)}
        whileHover={reduce ? undefined : { scale: 1.01 }}
        whileTap={reduce ? undefined : { scale: 0.99 }}
        transition={{ duration: DUR.fast, ease: EASE_OUT }}
        aria-haspopup="listbox"
        aria-expanded={open}
        className="flex w-full min-w-[240px] items-center gap-2.5 rounded-lg border border-line bg-surface/60 px-3 py-2.5 text-left text-sm text-ink backdrop-blur-sm transition-colors duration-150 hover:border-surface-3 hover:bg-surface-2 sm:w-auto"
      >
        {selected ? (
          <>
            <TeamLogo
              logo={selected.logo}
              name={LEAGUE_LOGO_FALLBACK[selected.id] ?? selected.name}
              kind="leagues"
              size={22}
              alt={selected.name}
            />
            <span className="min-w-0 flex-1 truncate font-medium">{selected.name}</span>
            <span className="text-xs text-ink-faint">{countryFlag(selected.country)}</span>
          </>
        ) : (
          <>
            <Trophy className="h-4 w-4 shrink-0 text-ink-faint" strokeWidth={2.25} />
            <span className="flex-1 text-ink-muted">{label ?? "Liqa seçin…"}</span>
          </>
        )}
        <motion.span
          animate={{ rotate: open ? 180 : 0 }}
          transition={{ duration: DUR.fast, ease: EASE_OUT }}
          className="text-ink-faint"
        >
          <ChevronDown className="h-4 w-4" strokeWidth={2.25} />
        </motion.span>
      </motion.button>

      <AnimatePresence>
        {open && (
          <motion.div
            key="league-dropdown"
            initial={reduce ? false : { opacity: 0, y: -6, scale: 0.98 }}
            animate={{ opacity: 1, y: 0, scale: 1 }}
            exit={reduce ? undefined : { opacity: 0, y: -6, scale: 0.98 }}
            transition={{ duration: DUR.fast, ease: EASE_OUT }}
            role="listbox"
            className="absolute left-0 z-30 mt-2 max-h-80 w-full min-w-[260px] overflow-y-auto rounded-xl border border-line bg-surface/95 p-1.5 backdrop-blur-md sm:w-72"
          >
            {leagues.length === 0 ? (
              <p className="px-3 py-6 text-center text-sm text-ink-faint">
                Liqa tapılmadı
              </p>
            ) : (
              leagues.map((league) => {
                const isSel = league.id === value;
                return (
                  <button
                    key={league.id}
                    onClick={() => {
                      onChange(league.id);
                      setOpen(false);
                    }}
                    role="option"
                    aria-selected={isSel}
                    className={cn(
                      "flex w-full items-center gap-2.5 rounded-lg px-2.5 py-2 text-left text-sm transition-colors duration-150",
                      isSel
                        ? "bg-brand/10 text-ink"
                        : "text-ink-muted hover:bg-surface-2 hover:text-ink",
                    )}
                  >
                    <TeamLogo
                      logo={league.logo}
                      name={LEAGUE_LOGO_FALLBACK[league.id] ?? league.name}
                      kind="leagues"
                      size={20}
                      alt={league.name}
                    />
                    <span className="min-w-0 flex-1 truncate">{league.name}</span>
                    {isSel && <span className="h-1.5 w-1.5 shrink-0 rounded-full bg-brand" />}
                    <span className="shrink-0 text-xs">{countryFlag(league.country)}</span>
                  </button>
                );
              })
            )}
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}
