"use client";

import { useCallback, useEffect, useState } from "react";
import { Radio } from "lucide-react";
import { FormComparison } from "@/app/predictions/components/FormComparison";
import { StandingsNeighborTable } from "@/app/predictions/components/StandingsNeighborTable";
import { TeamLogo } from "@/app/predictions/components/TeamLogo";
import { EmptyState } from "@/components/EmptyState";
import { api } from "@/lib/api";
import type { League, Match, TeamXGStats } from "@/types/football";

/**
 * Canlı / nəzərdə tutulan matçlar — /api/matches/live mənbəyindən.
 * Hər matçın komandası üçün son 5 oyun və cədvəl vəziyyəti göstərilir.
 */
export function LiveMatches({ teams }: { teams: TeamXGStats[] }) {
  const [matches, setMatches] = useState<Match[]>([]);
  const [loading, setLoading] = useState(true);

  const load = useCallback(() => {
    api
      .liveMatches()
      .then(setMatches)
      .catch(() => setMatches([]))
      .finally(() => setLoading(false));
  }, []);

  useEffect(() => {
    load();
    // status-live SSE deyil (sadə JSON), ona görə 30 saniyədə yenilənir
    const timer = setInterval(load, 30_000);
    return () => clearInterval(timer);
  }, [load]);

  if (loading) {
    return (
      <div className="space-y-2">
        {[0, 1].map((i) => (
          <div key={i} className="h-20 animate-pulse rounded-[14px] bg-surface" />
        ))}
      </div>
    );
  }

  if (matches.length === 0) {
    return (
      <EmptyState
        icon={Radio}
        title="Canlı matç yoxdur"
        description="İndilikdə oyun keçirilmir və ya bazada canlı oyun məlumatı yoxdur."
      />
    );
  }

  return (
    <div className="space-y-2">
      {matches.map((m) => (
        <article key={m.id} className="card p-3">
          <div className="flex items-center justify-between gap-3">
            <div className="flex min-w-0 items-center gap-2 text-[11px] text-ink-faint">
              <Radio className="h-3.5 w-3.5 text-brand" />
              <span className="truncate font-medium text-ink-muted">{m.league_name}</span>
            </div>
            <span className="shrink-0 text-xs text-ink-faint">{m.date}</span>
          </div>

          <div className="mt-2.5 grid min-w-0 grid-cols-[1fr_auto_1fr] items-center gap-2">
            <div className="flex min-w-0 items-center justify-end gap-2">
              <span className="truncate text-sm font-semibold text-ink">{m.home_team}</span>
              <span className="shrink-0 text-[10px] tabular-nums text-ink-faint">
                {m.home_team_position || ""}
              </span>
              <TeamLogo logo={m.home_logo} name={m.home_team} size={26} alt={m.home_team} />
            </div>

            <span className="rounded-md bg-surface-2 px-2 py-1 text-xs font-bold tabular-nums text-ink">
              {m.score ?? "VS"}
            </span>

            <div className="flex min-w-0 items-center gap-2">
              <TeamLogo logo={m.away_logo} name={m.away_team} size={26} alt={m.away_team} />
              <span className="shrink-0 text-[10px] tabular-nums text-ink-faint">
                {m.away_team_position || ""}
              </span>
              <span className="truncate text-sm font-semibold text-ink">{m.away_team}</span>
            </div>
          </div>

          {m.home_xg > 0 || m.away_xg > 0 ? (
            <div className="mt-2 flex items-center justify-center gap-3 text-[11px] tabular-nums text-ink-faint">
              <span>xG</span>
              <span className="font-bold text-ink">{m.home_xg.toFixed(2)}</span>
              <span>—</span>
              <span className="font-bold text-ink">{m.away_xg.toFixed(2)}</span>
            </div>
          ) : null}

          <FormComparison
            homeTeam={m.home_team}
            homeLast5={m.home_last5}
            awayTeam={m.away_team}
            awayLast5={m.away_last5}
          />

          {teams.length > 0 && (
            <div className="mt-2">
              <StandingsNeighborTable
                homeTeam={m.home_team}
                awayTeam={m.away_team}
                teams={teams}
              />
            </div>
          )}
        </article>
      ))}
    </div>
  );
}

export interface SchedulePageProps {
  leagues: League[];
}
