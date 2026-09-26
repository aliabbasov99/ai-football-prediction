import { InlineChip } from "./InlineChip";
import type { CouponSelection } from "@/components/couponUtils";
import type { PredictionItem } from "@/types/football";
import { matchKey } from "./utils";

/** BTTS (Bəli / Xeyr) — misli.az əmsalları + betimate faizləri. */
export function BttsBox({
  item,
  addToCoupon,
  isSelected,
}: {
  item: PredictionItem;
  addToCoupon: (sel: CouponSelection) => void;
  isSelected: (key: string) => boolean;
}) {
  const p = item.predictions;
  const btts = p?.misli_odds?.btts;
  const betimate = p?.betimate_stats;
  if (!btts?.yes && !btts?.no) return null;

  const mk = matchKey(item);
  const base = {
    matchKey: mk,
    marketLabel: "BTTS",
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
        BTTS
      </p>
      <div className="flex flex-wrap items-center gap-1.5">
        <InlineChip
          label="Bəli"
          value={btts.yes}
          selected={isSelected(`${mk}|btts_yes`)}
          onClick={() =>
            addToCoupon({
              ...base,
              key: `${mk}|btts_yes`,
              marketKey: "btts_yes",
              selection: "Bəli",
              odds: btts.yes ?? "",
            })
          }
        />
        <InlineChip
          label="Xeyr"
          value={btts.no}
          selected={isSelected(`${mk}|btts_no`)}
          onClick={() =>
            addToCoupon({
              ...base,
              key: `${mk}|btts_no`,
              marketKey: "btts_no",
              selection: "Xeyr",
              odds: btts.no ?? "",
            })
          }
        />
        {betimate?.btts_yes && (
          <span className="ml-auto text-[10px] text-ink-faint">
            Betimate: {betimate.btts_yes} / {betimate.btts_no}
          </span>
        )}
      </div>
    </div>
  );
}
