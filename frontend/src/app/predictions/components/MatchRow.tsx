"use client";

import { ChevronDown, ExternalLink } from "lucide-react";
import { useState } from "react";
import { TeamLogo } from "./TeamLogo";
import { BttsBox } from "./BttsBox";
import { OverUnderBox } from "./OverUnderBox";
import { PredictionsBox } from "./PredictionsBox";
import { WinProbabilityBox } from "./WinProbabilityBox";
import { UpcomingAndTopScorers } from "./UpcomingAndTopScorers";
import { LockIcon } from "./LockIcon";
import { InlineChip } from "./InlineChip";
import { availableSources, matchKey, type SourceInfo } from "./utils";
import type { CouponSelection } from "@/components/couponUtils";
import type { PredictionItem } from "@/types/football";
import { cn, formatDate } from "@/lib/utils";

interface MatchRowProps {
  item: PredictionItem;
  activeMarkets: Set<string>;
  addToCoupon: (sel: CouponSelection) => void;
  isSelected: (key: string) => boolean;
}

export function MatchRow({ item, activeMarkets, addToCoupon, isSelected }: MatchRowProps) {
  const [open, setOpen] = useState(false);
  const misli = item.predictions?.misli_odds;
  const sources: SourceInfo[] = availableSources(item.predictions);
  const activeSources = sources.filter((s) => s.has);

  const show1x2 = activeMarkets.has("1x2");
  const showDc = activeMarkets.has("dc");
  const showOu = activeMarkets.has("ou25");
  const showBtts = activeMarkets.has("btts");
  const hasAnyMarket = show1x2 || showDc || showOu || showBtts;

  const mk = matchKey(item);
  const base = {
    matchKey: mk,
    leagueName: item.league_name,
    homeTeam: item.home_team,
    awayTeam: item.away_team,
    homeLogo: item.home_logo,
    awayLogo: item.away_logo,
    date: item.date,
    time: item.time,
  };

  const canExpand =
    Boolean(item.predictions?.betimate_upcoming) ||
    Boolean(item.predictions?.top_scorers?.length) ||
    Boolean(item.predictions?.footystats_stats);

  return (
    <div className="card card-hover overflow-hidden">
      <div className="flex flex-col gap-3 p-3 lg:flex-row lg:items-center">
        {/* Vaxt */}
        <div className="flex shrink-0 items-center gap-2 text-xs text-ink-faint lg:w-24 lg:flex-col lg:items-start lg:gap-0.5">
          <span className="font-semibold text-ink">{item.time_az || item.time || "—"}</span>
          <span>{formatDate(item.date_az || item.date)}</span>
        </div>

        {/* Komandalar */}
        <div className="grid min-w-0 flex-1 grid-cols-[1fr_auto_1fr] items-center gap-2">
          <div className="flex min-w-0 items-center justify-end gap-2">
            <span className="truncate text-sm font-semibold text-ink">{item.home_team}</span>
            <TeamLogo logo={item.home_logo} name={item.home_team} size={26} alt={item.home_team} />
          </div>
          <span className="text-xs font-bold text-ink-faint">VS</span>
          <div className="flex min-w-0 items-center gap-2">
            <TeamLogo logo={item.away_logo} name={item.away_team} size={26} alt={item.away_team} />
            <span className="truncate text-sm font-semibold text-ink">{item.away_team}</span>
          </div>
        </div>

        {/* Əmsallar */}
        <div className="flex flex-wrap items-center gap-1.5 lg:w-80 lg:justify-end">
          {show1x2 && misli && (
            <>
              <InlineChip
                label="1"
                value={misli.home_win}
                selected={isSelected(`${mk}|home_win`)}
                onClick={() =>
                  addToCoupon({
                    ...base,
                    key: `${mk}|home_win`,
                    marketKey: "home_win",
                    marketLabel: "1X2",
                    selection: "1",
                    odds: misli.home_win ?? "",
                  })
                }
              />
              <InlineChip
                label="X"
                value={misli.draw}
                selected={isSelected(`${mk}|draw`)}
                onClick={() =>
                  addToCoupon({
                    ...base,
                    key: `${mk}|draw`,
                    marketKey: "draw",
                    marketLabel: "1X2",
                    selection: "X",
                    odds: misli.draw ?? "",
                  })
                }
              />
              <InlineChip
                label="2"
                value={misli.away_win}
                selected={isSelected(`${mk}|away_win`)}
                onClick={() =>
                  addToCoupon({
                    ...base,
                    key: `${mk}|away_win`,
                    marketKey: "away_win",
                    marketLabel: "1X2",
                    selection: "2",
                    odds: misli.away_win ?? "",
                  })
                }
              />
            </>
          )}

          {showDc && misli?.double_chance && (
            <InlineChip
              label="DC"
              value={[misli.double_chance["1X"], misli.double_chance["12"], misli.double_chance.X2]
                .filter(Boolean)
                .join(" / ")}
            />
          )}
        </div>

        {/* Mənbə badicələri */}
        <div className="flex shrink-0 items-center gap-1.5">
          {activeSources.map((source) =>
            source.href ? (
              <a
                key={source.id}
                href={source.href}
                target="_blank"
                rel="noopener noreferrer"
                title={`${source.label} — səhifəni aç`}
                className="rounded-md bg-surface-2 px-1.5 py-0.5 text-[10px] font-medium text-ink-faint transition-colors hover:text-info"
              >
                <ExternalLink className="h-3 w-3" />
              </a>
            ) : (
              <span
                key={source.id}
                title={source.label}
                className="rounded-md bg-surface-2 px-1.5 py-0.5 text-[10px] font-medium text-ink-faint"
              >
                {source.label.slice(0, 2).toUpperCase()}
              </span>
            ),
          )}

          {canExpand && (
            <button
              onClick={() => setOpen((v) => !v)}
              className="grid h-6 w-6 place-items-center rounded-md bg-surface-2 text-ink-faint transition-colors hover:text-ink"
              aria-label={open ? "Bağla" : "Aç"}
            >
              <ChevronDown className={cn("h-3.5 w-3.5 transition-transform", open && "rotate-180")} />
            </button>
          )}
        </div>
      </div>

      {/* Əlavə sətirlər */}
      {hasAnyMarket && (showOu || showBtts) && (
        <div className="grid gap-2 border-t border-line-soft p-3 sm:grid-cols-2">
          {showOu && <OverUnderBox item={item} addToCoupon={addToCoupon} isSelected={isSelected} />}
          {showBtts && <BttsBox item={item} addToCoupon={addToCoupon} isSelected={isSelected} />}
        </div>
      )}

      {open && (
        <div className="grid gap-2 border-t border-line-soft p-3 sm:grid-cols-2">
          <WinProbabilityBox item={item} />
          <PredictionsBox item={item} />
          <UpcomingAndTopScorers item={item} />

          {/* Baza açıldıqda heç bir məlumat yoxdursa */}
          {!activeSources.length && (
            <div className="rounded-lg border border-line-soft bg-surface-2 p-2 sm:col-span-2">
              <p className="mb-1.5 text-[10px] font-semibold uppercase tracking-wide text-ink-faint">
                Mənbə məlumatı
              </p>
              <div className="flex items-center gap-2 text-[11px] text-ink-faint">
                <LockIcon title="Bu matç üçün mənbə məlumatı yoxdur" />
                <span>
                  Pipeline hələ bu matçı yığmayıb — əmsal və proqnoz yoxdur.
                </span>
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
