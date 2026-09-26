"use client";

import { Loader2 } from "lucide-react";
import { useEffect, useMemo, useState } from "react";
import { StatsSidebar, StatPageHeader } from "./components/StatsSidebar";
import { FilterBar } from "./components/FilterBar";
import { StatsTable } from "./components/StatsTable";
import { PredictionsTable } from "./components/PredictionsTable";
import { STAT_PAGES } from "./components/constants";
import { EmptyState } from "@/components/EmptyState";
import { api } from "@/lib/api";
import type { FootyStatsPage, FootyStatsTable } from "@/types/football";

/** Bütün stat səhifələrini yükləyib birləşdirir. */
export default function StatsPage() {
  const [pages, setPages] = useState<Record<string, FootyStatsPage>>({});
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [query, setQuery] = useState("");

  useEffect(() => {
    let cancelled = false;
    async function load() {
      setLoading(true);
      const collected: Record<string, FootyStatsPage> = {};
      const results = await Promise.allSettled(
        STAT_PAGES.map((meta) => api.footystatsPage(meta.slug)),
      );
      results.forEach((result, i) => {
        if (result.status === "fulfilled" && result.value) {
          collected[STAT_PAGES[i].slug] = result.value;
        }
      });
      if (!cancelled) {
        setPages(collected);
        setError(Object.keys(collected).length === 0 ? "empty" : null);
        setLoading(false);
      }
    }
    load();
    return () => {
      cancelled = true;
    };
  }, []);

  /** Bütün yüklənmiş səhifələrin cədvəllərini bir listədə birləşdirir. */
  const allTables = useMemo<FootyStatsTable[]>(
    () =>
      Object.values(pages).flatMap((page) =>
        (page.tables ?? []).map((table) => ({ ...table, title: `${page.page_title} — ${table.title}` })),
      ),
    [pages],
  );

  const filteredTables = useMemo(() => {
    const q = query.trim().toLowerCase();
    if (!q) return allTables;
    return allTables
      .map((table) => ({
        ...table,
        rows: table.rows.filter((row) => row.some((c) => c && String(c).toLowerCase().includes(q))),
      }))
      .filter((t) => t.rows.length > 0);
  }, [allTables, query]);

  const loadedCount = Object.keys(pages).length;

  return (
    <div className="grid gap-5 lg:grid-cols-[260px_1fr]">
      <StatsSidebar />

      <div className="space-y-4">
        <StatPageHeader
          title="Statistika"
          description="FootyStats-dan toplanan 16 statistika kateqoriyası."
        />

        {loading && (
          <div className="grid place-items-center py-20">
            <Loader2 className="h-6 w-6 animate-spin text-ink-faint" />
          </div>
        )}

        {!loading && error && (
          <EmptyState
            title="Statistika tapılmadı"
            description="Bazada footystats_pages kolleksiyası boşdur. Admin panelindən FootyStats pipeline-ini işə salın."
          />
        )}

        {!loading && !error && (
          <>
            <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
              <FilterBar value={query} onChange={setQuery} />
              <span className="shrink-0 text-xs text-ink-faint">
                {loadedCount}/{STAT_PAGES.length} səhifə · {filteredTables.length} cədvəl
              </span>
            </div>

            {filteredTables.length === 0 ? (
              <EmptyState title="Cədvəl tapılmadı" description="Axtarışı dəyişdirin." />
            ) : (
              <div className="space-y-4">
                {filteredTables.map((table, i) =>
                  /proqnoz|prediction/i.test(table.title) ? (
                    <PredictionsTable key={i} table={table} />
                  ) : (
                    <StatsTable key={i} table={table} />
                  ),
                )}
              </div>
            )}
          </>
        )}
      </div>
    </div>
  );
}
