"use client";

import { TeamLogo } from "./TeamLogo";
import { MatchRow } from "./MatchRow";
import { groupByLeague } from "./utils";
import { LEAGUE_LOGO_FALLBACK } from "@/lib/logo";
import type { CouponSelection } from "@/components/couponUtils";
import type { PredictionItem } from "@/types/football";

interface LeagueGroupProps {
  leagueName: string;
  items: PredictionItem[];
  activeMarkets: Set<string>;
  addToCoupon: (sel: CouponSelection) => void;
  isSelected: (key: string) => boolean;
}

export function LeagueGroup({
  leagueName,
  items,
  activeMarkets,
  addToCoupon,
  isSelected,
}: LeagueGroupProps) {
  return (
    <section className="space-y-2">
      <header className="flex items-center gap-2.5">
        <TeamLogo
          name={LEAGUE_LOGO_FALLBACK[leagueName] ?? leagueName}
          kind="leagues"
          size={22}
          alt={leagueName}
        />
        <h2 className="text-sm font-bold uppercase tracking-wide text-ink">{leagueName}</h2>
        <span className="rounded-full bg-surface-2 px-2 py-0.5 text-xs font-semibold text-ink-muted">
          {items.length}
        </span>
      </header>

      <div className="space-y-2">
        {items.map((item, i) => (
          <MatchRow
            key={`${item.home_team}-${item.away_team}-${item.date}-${i}`}
            item={item}
            activeMarkets={activeMarkets}
            addToCoupon={addToCoupon}
            isSelected={isSelected}
          />
        ))}
      </div>
    </section>
  );
}

export { groupByLeague };
