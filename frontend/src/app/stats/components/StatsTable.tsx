import { GreenScoreBadge } from "./GreenScoreBadge";
import { extractNumber } from "./constants";
import type { FootyStatsTable } from "@/types/football";

interface StatsTableProps {
  table: FootyStatsTable;
}

/**
 * FootyStats cədvəli. Sətirlərdəki "Score" sütunu ən yüksək dəyərə görə
 * yaşıl işarələnir (backend footystats_all kolleksiyasındakı "score" meyarlığı).
 */
export function StatsTable({ table }: StatsTableProps) {
  if (!table.headers?.length || !table.rows?.length) return null;

  // Hər sütunun maksimum reqem dəyərini tap (score sütunu üçün)
  const maxByColumn = new Map<number, number>();
  table.headers.forEach((header, colIndex) => {
    if (!/score|rate|pct|%|\/ ?game/i.test(header)) return;
    let max = 0;
    for (const row of table.rows) {
      const n = extractNumber(row[colIndex]);
      if (n !== null && n > max) max = n;
    }
    maxByColumn.set(colIndex, max);
  });

  return (
    <div className="card overflow-hidden">
      <div className="border-b border-line bg-surface-2 px-3 py-2.5">
        <h3 className="text-sm font-bold text-ink">{table.title}</h3>
      </div>
      <div className="max-h-[520px] overflow-auto">
        <table className="w-full min-w-[640px] text-sm">
          <thead className="sticky top-0 bg-surface-2">
            <tr className="border-b border-line text-left">
              {table.headers.map((header, i) => (
                <th key={i} className="whitespace-nowrap px-3 py-2 font-semibold text-ink-muted">
                  {header}
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {table.rows.map((row, rowIndex) => (
              <tr key={rowIndex} className="border-b border-line-soft last:border-0">
                {row.map((cell, colIndex) => {
                  const max = maxByColumn.get(colIndex);
                  const n = extractNumber(cell);
                  const isBest = max !== undefined && max > 0 && n === max;
                  return (
                    <td key={colIndex} className="whitespace-nowrap px-3 py-1.5">
                      {isBest ? <GreenScoreBadge value={cell} isBest /> : cell ?? "—"}
                    </td>
                  );
                })}
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
