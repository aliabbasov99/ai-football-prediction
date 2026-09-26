import { PercentBar } from "./PercentBar";
import { extractNumber } from "./constants";
import type { FootyStatsTable } from "@/types/football";

/**
 * "predictions" səhifəsi üçün xüsusi cədvəl — hər sətirdə
 * qələbə faizi sütunları bar ilə göstərilir.
 */
export function PredictionsTable({ table }: { table: FootyStatsTable }) {
  if (!table.headers?.length || !table.rows?.length) return null;

  const pctColumns = table.headers
    .map((h, i) => (/pct|%|win/i.test(h) ? i : -1))
    .filter((i) => i !== -1);

  return (
    <div className="card overflow-hidden">
      <div className="border-b border-line bg-surface-2 px-3 py-2.5">
        <h3 className="text-sm font-semibold text-ink">{table.title}</h3>
      </div>
      <div className="max-h-[520px] overflow-auto">
        <table className="w-full min-w-[760px] text-sm">
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
                  const isPct = pctColumns.includes(colIndex);
                  const n = extractNumber(cell);
                  if (isPct && n !== null) {
                    return (
                      <td key={colIndex} className="px-3 py-1.5">
                        <div className="flex items-center gap-2">
                          <span className="w-11 shrink-0 text-right text-xs tabular-nums text-ink-muted">
                            {n.toFixed(0)}%
                          </span>
                          <div className="w-20">
                            <PercentBar value={n} tone={n >= 50 ? "success" : "info"} />
                          </div>
                        </div>
                      </td>
                    );
                  }
                  return (
                    <td key={colIndex} className="whitespace-nowrap px-3 py-1.5 text-ink-muted">
                      {cell ?? "—"}
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
