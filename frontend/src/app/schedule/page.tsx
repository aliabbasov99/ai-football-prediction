"use client";

import { CalendarDays, Loader2, Radio } from "lucide-react";
import { useEffect, useMemo, useState } from "react";
import { LeagueSelector } from "@/components/LeagueSelector";
import { StandingsTable } from "@/components/StandingsTable";
import { EmptyState } from "@/components/EmptyState";
import { LiveMatches } from "./components/LiveMatches";
import { api } from "@/lib/api";
import { useLeagueTeams } from "@/lib/useLeagueTeams";
import type { League } from "@/types/football";

export default function SchedulePage() {
  const [leagues, setLeagues] = useState<League[]>([]);
  const [selected, setSelected] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);

  const { teams: rawTeams, error: teamsError, loading: loadingTeams } =
    useLeagueTeams(selected);
  const teams = useMemo(
    () => [...rawTeams].sort((a, b) => a.position - b.position),
    [rawTeams],
  );

  useEffect(() => {
    api
      .leagues()
      .then((data) => {
        setLeagues(data);
        if (data.length > 0) setSelected(data[0].id);
      })
      .catch(() => setLeagues([]))
      .finally(() => setLoading(false));
  }, []);

  return (
    <div className="space-y-5">
      <div className="flex flex-col gap-4 sm:flex-row sm:items-end sm:justify-between">
        <div>
          <h1 className="text-2xl font-bold tracking-tight">Liqa cədvəli</h1>
          <p className="mt-1 text-sm text-ink-muted">
            Mövsum vəziyyəti, forma və xal cədvəli.
          </p>
        </div>
        <LeagueSelector leagues={leagues} value={selected} onChange={setSelected} />
      </div>

      {loading && (
        <div className="grid place-items-center py-20">
          <Loader2 className="h-6 w-6 animate-spin text-ink-faint" />
        </div>
      )}

      {!loading && leagues.length === 0 && (
        <EmptyState
          icon={CalendarDays}
          title="Liqa tapılmadı"
          description="Cədvəl üçün əvvəlcə liqa əlavə edilməlidir."
        />
      )}

      {loadingTeams && (
        <div className="grid place-items-center py-16">
          <Loader2 className="h-5 w-5 animate-spin text-ink-faint" />
        </div>
      )}

      {!loadingTeams && teams.length > 0 && (
        <>
          <div className="flex flex-wrap gap-x-5 gap-y-1 text-xs text-ink-faint">
            <span className="flex items-center gap-1.5">
              <span className="inline-block h-3 w-1 rounded bg-brand" /> Çempionat / UCL
            </span>
            <span className="flex items-center gap-1.5">
              <span className="inline-block h-3 w-1 rounded bg-violet" /> Avropa
            </span>
            <span className="flex items-center gap-1.5">
              <span className="inline-block h-3 w-1 rounded bg-danger" /> Küçək
            </span>
          </div>
          <StandingsTable teams={teams} />
        </>
      )}

      {teamsError && !loadingTeams && (
        <EmptyState
          icon={CalendarDays}
          title="Cədvəl yüklənmədi"
          description={teamsError}
        />
      )}

      {!loadingTeams && !teamsError && !loading && leagues.length > 0 && teams.length === 0 && (
        <EmptyState
          icon={CalendarDays}
          title="Cədvəl boşdur"
          description="Bu liqa üçün standings hələ toplanmayıb."
        />
      )}

      {/* Canlı / nəzərdə tutulan matçlar */}
      <section className="space-y-3 pt-2">
        <h2 className="flex items-center gap-2 text-sm font-bold uppercase tracking-wide text-ink">
          <Radio className="h-4 w-4 text-brand" /> Canlı matçlar
        </h2>
        <LiveMatches teams={teams} />
      </section>
    </div>
  );
}
