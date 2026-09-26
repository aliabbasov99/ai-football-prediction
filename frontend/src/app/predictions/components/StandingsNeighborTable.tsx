import { TeamLogo } from "./TeamLogo";
import type { TeamXGStats } from "@/types/football";

/** Matçdakı komandaların cədvəl yeri və ətraf komandalar. */
export function StandingsNeighborTable({
  homeTeam,
  awayTeam,
  teams,
}: {
  homeTeam: string;
  awayTeam: string;
  teams: TeamXGStats[];
}) {
  if (teams.length === 0) return null;

  const pick = (name: string) => teams.find((t) => t.team_name === name);

  const rows = [pick(homeTeam), pick(awayTeam)].filter(Boolean) as TeamXGStats[];
  if (rows.length === 0) return null;

  return (
    <div className="rounded-lg border border-line-soft bg-surface-2 p-2">
      <p className="mb-1.5 text-[10px] font-semibold uppercase tracking-wide text-ink-faint">
        Cədvəl vəziyyəti
      </p>
      <ul className="space-y-1">
        {rows.map((team) => (
          <li key={team.team_id || team.team_name} className="flex items-center gap-2 text-[11px]">
            <span className="w-5 shrink-0 text-right tabular-nums text-ink-faint">
              {team.position}
            </span>
            <TeamLogo logo={team.team_logo} name={team.team_name} size={16} alt={team.team_name} />
            <span className="min-w-0 flex-1 truncate text-ink">{team.team_name}</span>
            <span className="shrink-0 tabular-nums font-bold text-ink-muted">{team.points} xal</span>
          </li>
        ))}
      </ul>
    </div>
  );
}
