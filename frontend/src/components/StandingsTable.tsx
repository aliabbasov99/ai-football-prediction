"use client";

import { FormBadge } from "@/app/predictions/components/FormBadge";
import { TeamLogo } from "@/app/predictions/components/TeamLogo";
import type { TeamXGStats } from "@/types/football";
import { cn } from "@/lib/utils";

/** Liqa cədvəli. xG sütunları yoxdur — bu, cədvəlin təmiz versiyasıdır. */
export function StandingsTable({ teams }: { teams: TeamXGStats[] }) {
  if (teams.length === 0) return null;

  // Çempion / küçək zonları üçün rəng
  const max = teams.length;
  const zone = (pos: number) => {
    if (pos <= 4) return "border-l-brand"; // UCL
    if (pos <= 6) return "border-l-violet"; // Avropa
    if (pos > max - 3) return "border-l-danger"; // küçək
    return "border-l-transparent";
  };

  return (
    <div className="card overflow-hidden">
      <div className="overflow-x-auto">
        <table className="w-full min-w-[720px] text-sm">
          <thead>
            <tr className="border-b border-line bg-surface-2 text-left">
              <th className="px-3 py-2.5 font-semibold text-ink-muted">#</th>
              <th className="px-3 py-2.5 font-semibold text-ink-muted">Komanda</th>
              <th className="px-3 py-2.5 text-center font-semibold text-ink-muted">O</th>
              <th className="px-3 py-2.5 text-center font-semibold text-ink-muted">Q</th>
              <th className="px-3 py-2.5 text-center font-semibold text-ink-muted">H</th>
              <th className="px-3 py-2.5 text-center font-semibold text-ink-muted">M</th>
              <th className="px-3 py-2.5 text-center font-semibold text-ink-muted">+/-</th>
              <th className="px-3 py-2.5 text-center font-semibold text-ink-muted">Xal</th>
              <th className="px-3 py-2.5 font-semibold text-ink-muted">Forma</th>
            </tr>
          </thead>
          <tbody>
            {teams.map((team) => (
              <tr
                key={team.team_id || team.team_name}
                className={cn(
                  "card-hover border-b border-l-2 last:border-b-0",
                  zone(team.position),
                )}
              >
                <td className="px-3 py-2.5 tabular-nums font-semibold text-ink-faint">
                  {team.position}
                </td>
                <td className="px-3 py-2.5">
                  <div className="flex items-center gap-2">
                    <TeamLogo logo={team.team_logo} name={team.team_name} size={22} alt={team.team_name} />
                    <span className="font-medium text-ink">{team.team_name}</span>
                  </div>
                </td>
                <td className="px-3 py-2.5 text-center tabular-nums text-ink-muted">
                  {team.won + team.drawn + team.lost}
                </td>
                <td className="px-3 py-2.5 text-center tabular-nums text-ink-muted">{team.won}</td>
                <td className="px-3 py-2.5 text-center tabular-nums text-ink-muted">{team.drawn}</td>
                <td className="px-3 py-2.5 text-center tabular-nums text-ink-muted">{team.lost}</td>
                <td className="px-3 py-2.5 text-center tabular-nums text-ink-muted">
                  {team.goal_difference}
                </td>
                <td className="px-3 py-2.5 text-center tabular-nums font-bold text-ink">
                  {team.points}
                </td>
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
