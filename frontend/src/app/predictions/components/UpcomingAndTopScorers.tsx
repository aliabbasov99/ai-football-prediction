import { TeamLogo } from "./TeamLogo";
import type { PredictionItem, TopScorer, UpcomingMatch } from "@/types/football";

function UpcomingList({ games, title }: { games: UpcomingMatch[]; title: string }) {
  if (games.length === 0) return null;
  return (
    <div>
      <p className="mb-1 text-[10px] text-ink-faint">{title}</p>
      <ul className="space-y-0.5">
        {games.slice(0, 3).map((g, i) => (
          <li key={i} className="truncate text-[11px] text-ink-muted">
            {g.home} — {g.away}
            {g.score ? <span className="ml-1 font-semibold text-ink">{g.score}</span> : null}
          </li>
        ))}
      </ul>
    </div>
  );
}

/** Betimate-dan gələn növbəti oyunlar və ən yaxşı qolçular. */
export function UpcomingAndTopScorers({ item }: { item: PredictionItem }) {
  const p = item.predictions;
  if (!p) return null;

  const upcoming = p.betimate_upcoming;
  const scorers: TopScorer[] = p.top_scorers ?? [];
  const hasUpcoming = upcoming && (upcoming.home?.length || upcoming.away?.length);

  if (!hasUpcoming && scorers.length === 0) return null;

  return (
    <div className="rounded-lg border border-line-soft bg-surface-2 p-2">
      <p className="mb-1.5 text-[10px] font-semibold uppercase tracking-wider text-ink-faint">
        Əlavə məlumat
      </p>
      <div className="space-y-2">
        {hasUpcoming && (
          <div className="grid grid-cols-2 gap-2">
            <UpcomingList games={upcoming.home} title={`${item.home_team} — növbəti`} />
            <UpcomingList games={upcoming.away} title={`${item.away_team} — növbəti`} />
          </div>
        )}

        {scorers.length > 0 && (
          <div>
            <p className="mb-1 text-[10px] text-ink-faint">Ən yaxşı qolçular</p>
            <ul className="space-y-0.5">
              {scorers.slice(0, 3).map((s, i) => (
                <li key={i} className="flex items-center gap-1.5 text-[11px]">
                  {s.team_logo && <TeamLogo logo={s.team_logo} name={s.team} size={14} alt={s.team ?? ""} />}
                  <span className="min-w-0 flex-1 truncate text-ink-muted">{s.name}</span>
                  <span className="shrink-0 tabular-nums font-semibold text-ink">{s.goals}</span>
                </li>
              ))}
            </ul>
          </div>
        )}
      </div>
    </div>
  );
}
