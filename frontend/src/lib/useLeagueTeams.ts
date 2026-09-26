"use client";

import { useEffect, useState } from "react";
import { api } from "@/lib/api";
import type { TeamXGStats } from "@/types/football";

interface TeamsState {
  /** Nəticə hansı liqaya aiddir (köhnə nəticəni aşmaq üçün) */
  leagueId: string | null;
  teams: TeamXGStats[];
  error: string | null;
}

export interface LeagueTeamsResult {
  teams: TeamXGStats[];
  error: string | null;
  /** Yeni liqa seçilib, cavab hələ gəlməyib */
  loading: boolean;
}

/**
 * Seçili liqanın komanda statistikasını yükləyir.
 *
 * Nəticə `leagueId` ilə birgə saxlanılır: liqa dəyişən kimi əvvəlki
 * nəticə "köhnə" işarələnir, beləliklə səhifə heç vaxt əvvəlki liqanın
 * komandalarını yeni liqanın adı altında göstərmir.
 *
 * Bütün `setState` çağırışları `.then()`/`.catch()` callback-ləri daxilindədir —
 * React 19-un `set-state-in-effect` qaydası pozulmur.
 */
export function useLeagueTeams(leagueId: string | null): LeagueTeamsResult {
  const [state, setState] = useState<TeamsState>({
    leagueId,
    teams: [],
    error: null,
  });

  useEffect(() => {
    if (!leagueId) return;
    let cancelled = false;

    api
      .leagueTeams(leagueId)
      .then((teams) => {
        if (!cancelled) setState({ leagueId, teams, error: null });
      })
      .catch((e: unknown) => {
        if (!cancelled) {
          setState({
            leagueId,
            teams: [],
            error: e instanceof Error ? e.message : "Xəta baş verdi",
          });
        }
      });

    return () => {
      cancelled = true;
    };
  }, [leagueId]);

  const fresh = state.leagueId === leagueId;

  return {
    teams: fresh ? state.teams : [],
    error: fresh ? state.error : null,
    loading: !leagueId || !fresh,
  };
}
