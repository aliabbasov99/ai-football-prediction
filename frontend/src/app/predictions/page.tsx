"use client";

import { Filter, Loader2, TrendingUp } from "lucide-react";
import { useEffect, useMemo, useState } from "react";
import { LeagueGroup } from "@/app/predictions/components/LeagueGroup";
import { groupByLeague, hasMarket } from "@/app/predictions/components/utils";
import { OddsHeader } from "@/app/predictions/components/OddsHeader";
import { type MarketKey } from "./components/types";
import { EmptyState } from "@/components/EmptyState";
import { useCoupon } from "@/context/CouponContext";
import { api } from "@/lib/api";
import type { PredictionItem } from "@/types/football";

const ALL_MARKETS: MarketKey[] = ["1x2", "dc", "ou25", "btts"];

export default function PredictionsPage() {
  const [items, setItems] = useState<PredictionItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [markets, setMarkets] = useState<Set<string>>(new Set(ALL_MARKETS));
  const [leagueFilter, setLeagueFilter] = useState<string>("all");
  const { toggle, has } = useCoupon();

  useEffect(() => {
    api
      .predictions()
      .then(setItems)
      .catch((e) => setError(e.message))
      .finally(() => setLoading(false));
  }, []);

  function toggleMarket(key: string) {
    setMarkets((prev) => {
      const next = new Set(prev);
      if (next.has(key)) next.delete(key);
      else next.add(key);
      return next;
    });
  }

  const leagues = useMemo(
    () => Array.from(new Set(items.map((i) => i.league_name).filter(Boolean))).sort(),
    [items],
  );

  const grouped = useMemo(() => {
    const filtered =
      leagueFilter === "all" ? items : items.filter((i) => i.league_name === leagueFilter);
    return groupByLeague(filtered);
  }, [items, leagueFilter]);

  // Yalnız seçilmiş bazarlarda həqiqətən məlumatı olan matçları göstər
  const visible = useMemo(() => {
    const activeMarkets = Array.from(markets) as MarketKey[];
    const out = new Map<string, PredictionItem[]>();
    for (const [league, list] of grouped) {
      const filtered = list.filter((item) =>
        activeMarkets.some((m) => hasMarket(item.predictions, m)),
      );
      if (filtered.length > 0) out.set(league, filtered);
    }
    return out;
  }, [grouped, markets]);

  const totalVisible = Array.from(visible.values()).reduce((a, l) => a + l.length, 0);

  return (
    <div className="space-y-5">
      <div className="flex flex-col gap-4 lg:flex-row lg:items-end lg:justify-between">
        <div>
          <h1 className="text-2xl font-bold tracking-tight">Proqnozlar</h1>
          <p className="mt-1 text-sm text-ink-muted">
            Əmsal və proqnozlar 7+ mənbədən toplanır. Əmsala klikləyib kupon əlavə edin.
          </p>
        </div>

        <div className="flex flex-wrap items-center gap-2">
          <select
            value={leagueFilter}
            onChange={(e) => setLeagueFilter(e.target.value)}
            className="rounded-lg border border-line bg-surface px-3 py-2 text-sm text-ink outline-none focus:border-brand"
          >
            <option value="all">Bütün liqalar</option>
            {leagues.map((l) => (
              <option key={l} value={l}>
                {l}
              </option>
            ))}
          </select>
          <OddsHeader active={markets} onToggle={toggleMarket} />
        </div>
      </div>

      {loading && (
        <div className="grid place-items-center py-20">
          <Loader2 className="h-6 w-6 animate-spin text-ink-faint" />
        </div>
      )}

      {error && !loading && (
        <EmptyState
          icon={Filter}
          title="Məlumat yüklənmədi"
          description={error}
        />
      )}

      {!loading && !error && items.length === 0 && (
        <EmptyState
          icon={TrendingUp}
          title="Proqnoz tapılmadı"
          description="Bazada gələcək matç yoxdur. Admin panelindən pipeline-i işə salın."
        />
      )}

      {!loading && items.length > 0 && totalVisible === 0 && (
        <EmptyState
          icon={Filter}
          title="Seçilmiş bazarlarda məlumat yoxdur"
          description="Yuxarıdakı bazarları dəyişdirib yenidən yoxlayın."
        />
      )}

      <div className="space-y-6">
        {Array.from(visible.entries()).map(([league, list]) => (
          <LeagueGroup
            key={league}
            leagueName={league}
            items={list}
            activeMarkets={markets}
            addToCoupon={toggle}
            isSelected={has}
          />
        ))}
      </div>
    </div>
  );
}
