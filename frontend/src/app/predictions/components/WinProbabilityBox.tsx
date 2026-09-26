import type { PredictionItem } from "@/types/football";
import { percentValue } from "./utils";

/** Qələbə ehtimalı: betimate faizləri + oddslot + wincomparator. */
export function WinProbabilityBox({ item }: { item: PredictionItem }) {
  const p = item.predictions;
  if (!p) return null;

  const home = p.betimate_home_win ?? p.betimate_stats?.home_win;
  const draw = p.betimate_draw ?? p.betimate_stats?.draw;
  const away = p.betimate_away_win ?? p.betimate_stats?.away_win;

  const oddslotHome = p.oddslot_stats?.home_percent ?? p.oddslot_home_chance;
  const oddslotAway = p.oddslot_stats?.away_percent ?? p.oddslot_away_chance;
  const wcProb = p.wincomparator_stats?.["1x2"]?.probability;

  const hasBetimate = home || draw || away;
  if (!hasBetimate && !oddslotHome && !wcProb) return null;

  return (
    <div className="rounded-lg border border-line-soft bg-surface-2 p-2">
      <p className="mb-1.5 text-[10px] font-semibold uppercase tracking-wider text-ink-faint">
        Qələbə ehtimalı
      </p>

      {hasBetimate && (
        <div className="grid grid-cols-3 gap-1.5 text-center">
          {[
            { label: "1", value: home, tone: "text-success" },
            { label: "X", value: draw, tone: "text-ink-muted" },
            { label: "2", value: away, tone: "text-info" },
          ].map((cell) => (
            <div key={cell.label} className="rounded-md bg-surface px-1 py-1">
              <p className="text-[10px] text-ink-faint">{cell.label}</p>
              <p className={`text-xs font-semibold tabular-nums ${cell.tone}`}>
                {percentValue(cell.value)}
              </p>
            </div>
          ))}
        </div>
      )}

      {(oddslotHome || oddslotAway) && (
        <div className="mt-1.5 flex items-center justify-between text-[10px] text-ink-faint">
          <span>Oddslot</span>
          <span className="tabular-nums">
            <span className="text-success">{percentValue(oddslotHome)}</span>
            {" / "}
            <span className="text-info">{percentValue(oddslotAway)}</span>
          </span>
        </div>
      )}

      {wcProb && (
        <div className="mt-1 flex items-center justify-between text-[10px] text-ink-faint">
          <span>WinComparator</span>
          <span className="tabular-nums text-ink">{percentValue(wcProb)}</span>
        </div>
      )}
    </div>
  );
}
