"use client";

import { ChevronDown } from "lucide-react";
import { useEffect, useRef, useState } from "react";
import { TeamLogo } from "@/app/predictions/components/TeamLogo";
import { countryFlag } from "@/lib/countries";
import { LEAGUE_LOGO_FALLBACK } from "@/lib/logo";
import type { League } from "@/types/football";
import { cn } from "@/lib/utils";

interface LeagueSelectorProps {
  leagues: League[];
  value: string | null;
  onChange: (id: string) => void;
  label?: string;
}

export function LeagueSelector({ leagues, value, onChange, label }: LeagueSelectorProps) {
  const [open, setOpen] = useState(false);
  const ref = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (!open) return;
    function onClick(e: MouseEvent) {
      if (ref.current && !ref.current.contains(e.target as Node)) setOpen(false);
    }
    document.addEventListener("mousedown", onClick);
    return () => document.removeEventListener("mousedown", onClick);
  }, [open]);

  const selected = leagues.find((l) => l.id === value);

  return (
    <div ref={ref} className="relative">
      <button
        onClick={() => setOpen((v) => !v)}
        className="flex w-full min-w-[240px] items-center gap-2.5 rounded-lg border border-line bg-surface px-3 py-2.5 text-left text-sm transition-colors hover:bg-surface-2 sm:w-auto"
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
            <span className="min-w-0 flex-1 truncate font-medium">
              {selected.name}
            </span>
            <span className="text-xs text-ink-faint">{countryFlag(selected.country)}</span>
          </>
        ) : (
          <span className="flex-1 text-ink-muted">{label ?? "Liqa seçin…"}</span>
        )}
        <ChevronDown className={cn("h-4 w-4 shrink-0 text-ink-faint transition-transform", open && "rotate-180")} />
      </button>

      {open && (
        <div className="absolute left-0 z-30 mt-1.5 max-h-80 w-full min-w-[260px] overflow-y-auto rounded-lg border border-line bg-surface-2 p-1 shadow-xl sm:w-72">
          {leagues.length === 0 ? (
            <p className="px-3 py-6 text-center text-sm text-ink-faint">
              Liqa tapılmadı
            </p>
          ) : (
            leagues.map((league) => (
              <button
                key={league.id}
                onClick={() => {
                  onChange(league.id);
                  setOpen(false);
                }}
                className={cn(
                  "flex w-full items-center gap-2.5 rounded-md px-2.5 py-2 text-left text-sm transition-colors",
                  league.id === value
                    ? "bg-surface-3 text-ink"
                    : "text-ink-muted hover:bg-surface-3 hover:text-ink",
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
                <span className="shrink-0 text-xs">{countryFlag(league.country)}</span>
              </button>
            ))
          )}
        </div>
      )}
    </div>
  );
}
