"use client";

import { TeamLogo } from "@/app/predictions/components/TeamLogo";
import { FormBadge } from "@/app/predictions/components/FormBadge";
import type { TopBottomMatch, TopBottomTeam } from "@/types/football";
import { formatDate } from "@/lib/utils";

/** Top və ya bottom komandası üçün kart. */
export function TopBottomTeamCard({
  team,
  tone,
}: {
  team: TopBottomTeam;
  tone: "top" | "bottom";
}) {
  return (
    <div className="card card-hover flex items-center gap-3 p-3">
      <TeamLogo
        logo={team.team_logo}
        name={team.team_name}
        size={34}
        alt={team.team_name ?? ""}
      />
      <div className="min-w-0 flex-1">
        <p className="truncate text-sm font-semibold text-ink">{team.team_name}</p>
        <p className="truncate text-xs text-ink-faint">
          {team.league_name}
          {team.position ? ` · ${team.position}. yer` : ""}
        </p>
      </div>
      <div className="shrink-0 text-right">
        {typeof team.points === "number" && (
          <p className="text-sm font-bold tabular-nums text-ink">{team.points}</p>
        )}
        <p
          className={
            tone === "top"
              ? "text-[10px] font-semibold text-success"
              : "text-[10px] font-semibold text-danger"
          }
        >
          {tone === "top" ? "TOP" : "BOTTOM"}
        </p>
      </div>
    </div>
  );
}

/** Top — Bottom qarşılaşması. */
export function TopBottomMatchRow({ match }: { match: TopBottomMatch }) {
  return (
    <div className="card card-hover flex flex-col gap-2 p-3 sm:flex-row sm:items-center">
      <div className="shrink-0 text-xs text-ink-faint sm:w-28">
        {formatDate(match.date)} {match.time ?? ""}
      </div>

      <div className="grid min-w-0 flex-1 grid-cols-[1fr_auto_1fr] items-center gap-2">
        <div className="flex min-w-0 items-center justify-end gap-2">
          <span className="truncate text-sm font-semibold text-ink">
            {match.home_team}
          </span>
          {match.home_position ? (
            <span className="shrink-0 text-[10px] tabular-nums text-ink-faint">
              {match.home_position}.
            </span>
          ) : null}
          <TeamLogo
            logo={match.home_logo}
            name={match.home_team}
            size={24}
            alt={match.home_team}
          />
        </div>

        <span className="text-xs font-bold text-ink-faint">VS</span>

        <div className="flex min-w-0 items-center gap-2">
          <TeamLogo
            logo={match.away_logo}
            name={match.away_team}
            size={24}
            alt={match.away_team}
          />
          {match.away_position ? (
            <span className="shrink-0 text-[10px] tabular-nums text-ink-faint">
              {match.away_position}.
            </span>
          ) : null}
          <span className="truncate text-sm font-semibold text-ink">
            {match.away_team}
          </span>
        </div>
      </div>

      {match.league_name && (
        <span className="shrink-0 text-xs text-ink-faint">{match.league_name}</span>
      )}
    </div>
  );
}

/** Formaları yan-yana müqayisə edən kiçik sıra (top-bottom ehtiyatı üçün). */
export function FormRow({ form }: { form: string }) {
  return <FormBadge form={form} />;
}
