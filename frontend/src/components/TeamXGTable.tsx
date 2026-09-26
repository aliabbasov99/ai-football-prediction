"use client";

import { TeamLogo } from "@/app/predictions/components/TeamLogo";
import { FormBadge } from "@/app/predictions/components/FormBadge";
import type { GameStats, TeamXGStats } from "@/types/football";

function StatCell({ stats }: { stats?: GameStats }) {
  if (!stats || !stats.games) {
    return <span className="text-ink-faint">—</span>;
  }
  return (
    <span className="tabular-nums">
      <span className="font-semibold text-ink">{stats.xg_for.toFixed(2)}</span>
      <span className="text-ink-faint"> / {stats.xg_against.toFixed(2)}</span>
      <span className="ml-1 text-xs text-ink-faint">({stats.games})</span>
    </span>
  );
}

const COLUMNS = [
  { key: "last_30_games", label: "Son 30 oyun" },
  { key: "league_games", label: "Liqa" },
  { key: "cup_games", label: "Kubok" },
] as const;

export function TeamXGTable({ teams }: { teams: TeamXGStats[] }) {
  if (teams.length === 0) return null;

  return (
    <div className="card overflow-hidden">
      <div className="overflow-x-auto">
        <table className="w-full min-w-[820px] text-sm">
          <thead>
            <tr className="border-b border-line bg-surface-2 text-left">
              <th className="px-3 py-2.5 font-semibold text-ink-muted">#</th>
              <th className="px-3 py-2.5 font-semibold text-ink-muted">Komanda</th>
              {COLUMNS.map((col) => (
                <th key={col.key} className="px-3 py-2.5 text-right font-semibold text-ink-muted">
                  {col.label}
                </th>
              ))}
              <th className="px-3 py-2.5 text-right font-semibold text-ink-muted">O</th>
              <th className="px-3 py-2.5 text-right font-semibold text-ink-muted">Q</th>
              <th className="px-3 py-2.5 text-right font-semibold text-ink-muted">H</th>
              <th className="px-3 py-2.5 text-right font-semibold text-ink-muted">M</th>
              <th className="px-3 py-2.5 text-right font-semibold text-ink-muted">Xal</th>
              <th className="px-3 py-2.5 font-semibold text-ink-muted">Forma</th>
            </tr>
          </thead>
          <tbody>
            {teams.map((team) => (
              <tr
                key={team.team_id || team.team_name}
                className="card-hover border-b border-line-soft last:border-0"
              >
                <td className="px-3 py-2.5 tabular-nums text-ink-faint">{team.position}</td>
                <td className="px-3 py-2.5">
                  <div className="flex items-center gap-2">
                    <TeamLogo logo={team.team_logo} name={team.team_name} size={22} alt={team.team_name} />
                    <span className="font-medium text-ink">{team.team_name}</span>
                  </div>
                </td>
                {COLUMNS.map((col) => (
                  <td key={col.key} className="px-3 py-2.5 text-right">
                    <StatCell stats={team[col.key]} />
                  </td>
                ))}
                <td className="px-3 py-2.5 text-right tabular-nums text-ink-muted">{team.won}</td>
                <td className="px-3 py-2.5 text-right tabular-nums text-ink-muted">{team.drawn}</td>
                <td className="px-3 py-2.5 text-right tabular-nums text-ink-muted">{team.lost}</td>
                <td className="px-3 py-2.5 text-right tabular-nums font-bold text-ink">{team.points}</td>
                <td className="px-3 py-2.5">
                  <FormBadge form={team.form} />
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
