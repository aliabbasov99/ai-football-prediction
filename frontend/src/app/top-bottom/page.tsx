"use client";

import { Activity, Loader2, TrendingDown, TrendingUp } from "lucide-react";
import { useEffect, useState } from "react";
import {
  TopBottomMatchRow,
  TopBottomTeamCard,
} from "./components/TopBottomCards";
import { EmptyState } from "@/components/EmptyState";
import { api } from "@/lib/api";
import type { TopBottomMatch, TopBottomTeams } from "@/types/football";

export default function TopBottomPage() {
  const [teams, setTeams] = useState<TopBottomTeams | null>(null);
  const [matches, setMatches] = useState<TopBottomMatch[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    Promise.all([api.topBottomTeams(), api.topBottomMatches(50)])
      .then(([t, m]) => {
        setTeams(t);
        setMatches(m);
      })
      .catch((e) => setError(e.message))
      .finally(() => setLoading(false));
  }, []);

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold tracking-tight">Top vs Bottom</h1>
        <p className="mt-1 text-sm text-ink-muted">
          Cədvəlin yuxarı və aşağı hissəsindəki komandaların qarşılaşmaları.
        </p>
      </div>

      {loading && (
        <div className="grid place-items-center py-20">
          <Loader2 className="h-6 w-6 animate-spin text-ink-faint" />
        </div>
      )}

      {error && !loading && <EmptyState title="Məlumat yüklənmədi" description={error} />}

      {!loading && !error && (
        <>
          <div className="grid gap-4 lg:grid-cols-2">
            <section className="space-y-2">
              <h2 className="flex items-center gap-2 text-sm font-bold uppercase tracking-wide text-ink">
                <TrendingUp className="h-4 w-4 text-success" /> Top komandalar
              </h2>
              {teams?.top_teams?.length ? (
                <div className="space-y-2">
                  {teams.top_teams.map((t, i) => (
                    <TopBottomTeamCard key={`${t.team_name}-${i}`} team={t} tone="top" />
                  ))}
                </div>
              ) : (
                <EmptyState title="Top komanda yoxdur" />
              )}
            </section>

            <section className="space-y-2">
              <h2 className="flex items-center gap-2 text-sm font-bold uppercase tracking-wide text-ink">
                <TrendingDown className="h-4 w-4 text-danger" /> Bottom komandalar
              </h2>
              {teams?.bottom_teams?.length ? (
                <div className="space-y-2">
                  {teams.bottom_teams.map((t, i) => (
                    <TopBottomTeamCard key={`${t.team_name}-${i}`} team={t} tone="bottom" />
                  ))}
                </div>
              ) : (
                <EmptyState title="Bottom komanda yoxdur" />
              )}
            </section>
          </div>

          <section className="space-y-2">
            <h2 className="flex items-center gap-2 text-sm font-bold uppercase tracking-wide text-ink">
              <Activity className="h-4 w-4 text-info" /> Top — Bottom qarşılaşmaları
            </h2>
            {matches.length === 0 ? (
              <EmptyState title="Qarşılaşma tapılmadı" />
            ) : (
              <div className="space-y-2">
                {matches.map((m, i) => (
                  <TopBottomMatchRow key={`${m.home_team}-${m.away_team}-${i}`} match={m} />
                ))}
              </div>
            )}
          </section>
        </>
      )}
    </div>
  );
}
