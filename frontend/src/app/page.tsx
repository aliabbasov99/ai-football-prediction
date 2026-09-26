"use client";

import { Loader2, Search, Sigma } from "lucide-react";
import { useEffect, useMemo, useState } from "react";
import {
  SeriesLegend,
  StatCards,
  type StatCardItem,
} from "@/app/components/StatCards";
import { LeagueSelector } from "@/components/LeagueSelector";
import { TeamXGTable } from "@/components/TeamXGTable";
import { EmptyState } from "@/components/EmptyState";
import { Reveal } from "@/components/motion";
import { api } from "@/lib/api";
import { useLeagueTeams } from "@/lib/useLeagueTeams";
import type { League, PredictionItem } from "@/types/football";

export default function HomePage() {
  const [leagues, setLeagues] = useState<League[]>([]);
  const [selected, setSelected] = useState<string | null>(null);
  const [predictions, setPredictions] = useState<PredictionItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const { teams, error: teamsError, loading: loadingTeams } = useLeagueTeams(selected);

  useEffect(() => {
    api
      .leagues()
      .then((data) => {
        setLeagues(data);
        if (data.length > 0) setSelected(data[0].id);
      })
      .catch((e) => setError(e.message))
      .finally(() => setLoading(false));

    // Stat kartları üçün ümumi sayğaclar
    api.predictions().then(setPredictions).catch(() => setPredictions([]));
  }, []);

  const league = leagues.find((l) => l.id === selected);

  const cards = useMemo<StatCardItem[]>(() => {
    const withOdds = predictions.filter((p) => p.predictions?.misli_odds).length;
    const totalXg = teams.reduce((acc, t) => acc + (t.league_games?.xg_for ?? 0), 0);
    const totalGames = teams.reduce((acc, t) => acc + (t.league_games?.games ?? 0), 0);
    return [
      { label: "Aktiv liqa", value: leagues.length, tone: "brand" },
      { label: "Komanda", value: teams.length || "—", tone: "info" },
      { label: "Proqnozlu matç", value: predictions.length || "—", tone: "warn" },
      {
        label: "Əmsalı olan matç",
        value: withOdds || "—",
        hint: totalGames > 0 ? `${totalGames} oyun · xG ${totalXg.toFixed(1)}` : undefined,
        tone: "success",
      },
    ];
  }, [leagues.length, teams, predictions]);

  return (
    <div className="space-y-6">
      <Reveal>
        <div className="flex flex-col gap-4 sm:flex-row sm:items-end sm:justify-between">
          <div>
            <h1 className="flex items-center gap-2 text-2xl font-semibold tracking-tight">
              <Sigma className="h-5.5 w-5.5 text-brand" strokeWidth={2.25} />
              xG Analizi
            </h1>
            <p className="mt-1 text-sm text-ink-muted">
              Liqa seçin və komandaların gözlənilən qol statistikasını müqayisə edin.
            </p>
          </div>
          <LeagueSelector leagues={leagues} value={selected} onChange={setSelected} />
        </div>
      </Reveal>

      <StatCards items={cards} />

      {loading && (
        <div className="grid place-items-center py-20">
          <Loader2 className="h-6 w-6 animate-spin text-ink-faint" />
        </div>
      )}

      {error && !loading && (
        <EmptyState
          icon={Search}
          title="Backend ilə əlaqə qurulmadı"
          description={`${error} — backend-in :7999 portunda işlədiyindən əmin olun.`}
        />
      )}

      {!loading && !error && leagues.length === 0 && (
        <EmptyState
          title="Liqa tapılmadı"
          description="Bazada hələ liqa yoxdur. Admin panelindən liqa əlavə edin və ya pipeline-i işə salın."
        />
      )}

      {loadingTeams && (
        <div className="grid place-items-center py-16">
          <Loader2 className="h-5 w-5 animate-spin text-ink-faint" />
        </div>
      )}

      {!loadingTeams && teams.length > 0 && (
        <>
          <Reveal delay={0.1}>
            <div className="flex flex-wrap items-center gap-x-5 gap-y-1.5 text-xs text-ink-faint">
              <SeriesLegend extra={league?.name} />
              <span>{teams.length} komanda</span>
            </div>
          </Reveal>
          <Reveal delay={0.15}>
            <TeamXGTable teams={teams} />
          </Reveal>
        </>
      )}

      {teamsError && !loadingTeams && (
        <EmptyState
          icon={Search}
          title="Komanda siyahısı yüklənmədi"
          description={teamsError}
        />
      )}

      {!loadingTeams && !teamsError && !loading && leagues.length > 0 && teams.length === 0 && (
        <EmptyState
          title="Komanda məlumatı yoxdur"
          description={`${league?.name ?? "Bu liqa"} üçün standings hələ toplanmayıb. Pipeline-i işə salın.`}
        />
      )}
    </div>
  );
}
