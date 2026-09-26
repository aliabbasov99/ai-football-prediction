import { TeamLogo } from "./TeamLogo";
import type { Last5Game } from "@/types/football";
import { cn } from "@/lib/utils";

/** İki komandanın son 5 oyununun müqayisəsi. */
export function FormComparison({
  homeTeam,
  homeLast5 = [],
  awayTeam,
  awayLast5 = [],
}: {
  homeTeam: string;
  homeLast5?: Last5Game[];
  awayTeam: string;
  awayLast5?: Last5Game[];
}) {
  if (homeLast5.length === 0 && awayLast5.length === 0) return null;

  const row = (games: Last5Game[], align: "left" | "right") => (
    <div className={cn("flex gap-1", align === "right" && "flex-row-reverse")}>
      {games.slice(0, 5).map((g, i) => {
        const won = g.score ? Number(g.score.split("-")[0]) > Number(g.score.split("-")[1]) : false;
        const drew = g.score ? g.score.split("-")[0] === g.score.split("-")[1] : false;
        const tone = !g.score
          ? "bg-surface-3 text-ink-faint"
          : won
            ? "bg-success/20 text-success"
            : drew
              ? "bg-warn/20 text-warn"
              : "bg-danger/20 text-danger";
        return (
          <span
            key={i}
            title={`${g.home_away === "H" ? "Ev" : "Sahədən"} ${g.opponent} ${g.score ?? ""}`}
            className={cn("grid h-5 w-5 place-items-center rounded text-[10px] font-semibold", tone)}
          >
            {g.home_away}
          </span>
        );
      })}
    </div>
  );

  return (
    <div className="flex items-center justify-between gap-3 border-t border-line-soft pt-2">
      <div className="flex min-w-0 items-center gap-1.5">
        <TeamLogo name={homeTeam} size={16} alt={homeTeam} />
        {row(homeLast5, "left")}
      </div>
      <div className="flex min-w-0 items-center gap-1.5">
        {row(awayLast5, "right")}
        <TeamLogo name={awayTeam} size={16} alt={awayTeam} />
      </div>
    </div>
  );
}
