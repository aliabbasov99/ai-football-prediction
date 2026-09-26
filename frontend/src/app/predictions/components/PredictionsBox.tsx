import { ExternalLink, Target } from "lucide-react";
import type { PredictionItem } from "@/types/football";

/** Mənbə proqnozları: wincomparator, sportsgambler, betimate proqnozları. */
export function PredictionsBox({ item }: { item: PredictionItem }) {
  const p = item.predictions;
  if (!p) return null;

  const rows: Array<{ source: string; text: string; href?: string }> = [];

  if (p.wincomparator_stats) {
    const wc = p.wincomparator_stats;
    if (wc["1x2"]?.prediction) {
      rows.push({
        source: "WinComparator",
        text: `${wc["1x2"].prediction}${wc["1x2"].probability ? ` (${wc["1x2"].probability})` : ""}`,
        href: p.wincomparator_link,
      });
    }
    if (wc.under_over?.line) {
      rows.push({
        source: "WinComparator",
        text: `${wc.under_over.type === "over" ? "Over" : "Under"} ${wc.under_over.line.replace(/^[+-]/, "")} @ ${wc.under_over.odds ?? "?"}`,
        href: p.wincomparator_link,
      });
    }
  }

  if (p.sportsgambler_stats?.prediction) {
    rows.push({
      source: "SportsGambler",
      text: p.sportsgambler_stats.prediction,
      href: p.sportsgambler_link,
    });
  }
  if (p.sportsgambler_stats?.correct_score) {
    rows.push({
      source: "SportsGambler",
      text: `Top heç nə: ${p.sportsgambler_stats.correct_score}`,
      href: p.sportsgambler_link,
    });
  }

  if (p.betimate_score) {
    rows.push({ source: "Betimate", text: `Proqnoz: ${p.betimate_score}` });
  }

  if (rows.length === 0) return null;

  return (
    <div className="rounded-lg border border-line-soft bg-surface-2 p-2">
      <p className="mb-1.5 flex items-center gap-1 text-[10px] font-semibold uppercase tracking-wide text-ink-faint">
        <Target className="h-3 w-3" /> Proqnozlar
      </p>
      <ul className="space-y-1">
        {rows.map((row, i) => (
          <li key={i} className="flex items-start justify-between gap-2 text-[11px]">
            <span className="min-w-0 flex-1">
              <span className="text-ink-faint">{row.source}: </span>
              <span className="font-medium text-ink">{row.text}</span>
            </span>
            {row.href && (
              <a
                href={row.href}
                target="_blank"
                rel="noopener noreferrer"
                className="shrink-0 text-ink-faint transition-colors hover:text-info"
                aria-label="Mənbəyə aç"
              >
                <ExternalLink className="h-3 w-3" />
              </a>
            )}
          </li>
        ))}
      </ul>
    </div>
  );
}
