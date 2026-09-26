import { ArrowDown, ArrowUp } from "lucide-react";
import { InlineChip } from "./InlineChip";
import type { CouponSelection } from "@/components/couponUtils";
import type { PredictionItem } from "@/types/football";
import { matchKey, percentValue } from "./utils";

/** Over/Under 2.5 — misli əmsalları + betimate faizləri. */
export function OverUnderBox({
  item,
  addToCoupon,
  isSelected,
}: {
  item: PredictionItem;
  addToCoupon: (sel: CouponSelection) => void;
  isSelected: (key: string) => boolean;
}) {
  const p = item.predictions;
  const ou = p?.misli_odds?.over_under;
  const betimate = p?.betimate_stats;
  if (!ou?.over && !ou?.under) return null;

  const mk = matchKey(item);
  const base = {
    matchKey: mk,
    marketLabel: "Over/Under 2.5",
    leagueName: item.league_name,
    homeTeam: item.home_team,
    awayTeam: item.away_team,
    homeLogo: item.home_logo,
    awayLogo: item.away_logo,
    date: item.date,
    time: item.time,
  };

  return (
    <div className="rounded-lg border border-line-soft bg-surface-2 p-2">
      <p className="mb-1.5 text-[10px] font-semibold uppercase tracking-wide text-ink-faint">
        Over / Under 2.5
      </p>
      <div className="flex flex-wrap items-center gap-1.5">
        <InlineChip
          label="Over"
          value={ou.over}
          selected={isSelected(`${mk}|over`)}
          onClick={() =>
            addToCoupon({
              ...base,
              key: `${mk}|over`,
              marketKey: "over",
              selection: "Over",
              odds: ou.over ?? "",
            })
          }
        />
        <InlineChip
          label="Under"
          value={ou.under}
          selected={isSelected(`${mk}|under`)}
          onClick={() =>
            addToCoupon({
              ...base,
              key: `${mk}|under`,
              marketKey: "under",
              selection: "Under",
              odds: ou.under ?? "",
            })
          }
        />
        {(betimate?.over_2_5 || betimate?.under_2_5) && (
          <span className="ml-auto flex items-center gap-1 text-[10px] text-ink-faint">
            Betimate
            {betimate.over_2_5 && (
              <span className="flex items-center text-success">
                <ArrowUp className="h-2.5 w-2.5" />
                {percentValue(betimate.over_2_5)}
              </span>
            )}
            {betimate.under_2_5 && (
              <span className="flex items-center text-info">
                <ArrowDown className="h-2.5 w-2.5" />
                {percentValue(betimate.under_2_5)}
              </span>
            )}
          </span>
        )}
      </div>
    </div>
  );
}
