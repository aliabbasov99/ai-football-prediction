"use client";

import { motion, useReducedMotion } from "framer-motion";
import { Loader2 } from "lucide-react";
import { useEffect, useMemo, useState } from "react";
import { StatsSidebar, StatPageHeader } from "./components/StatsSidebar";
import { FilterBar } from "./components/FilterBar";
import { StatsTable } from "./components/StatsTable";
import { PredictionsTable } from "./components/PredictionsTable";
import { STAT_PAGES } from "./components/constants";
import { EmptyState } from "@/components/EmptyState";
import { Reveal, RevealItem, staggerList } from "@/components/motion";
import { api } from "@/lib/api";
import type { FootyStatsPage, FootyStatsTable } from "@/types/football";

/** Bütün stat səhifələrini yükləyib birləşdirir. */
export default function StatsPage() {
  const [pages, setPages] = useState<Record<string, FootyStatsPage>>({});
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [query, setQuery] = useState("");
  const reduce = useReducedMotion();

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
    <div className="grid gap-6 lg:grid-cols-[260px_1fr]">
      <Reveal>
        <StatsSidebar />
      </Reveal>

      <div className="space-y-6">
        <Reveal>
          <StatPageHeader
            title="Statistika"
            description="FootyStats-dan toplanan 16 statistika kateqoriyası."
          />
        </Reveal>

        {loading && (
          <div className="grid place-items-center py-20">
            <Loader2 className="h-6 w-6 animate-spin text-ink-faint" strokeWidth={2.25} />
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
            <Reveal delay={0.05}>
              <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
                <FilterBar value={query} onChange={setQuery} />
                <span className="shrink-0 text-xs text-ink-faint">
                  {loadedCount}/{STAT_PAGES.length} səhifə · {filteredTables.length} cədvəl
                </span>
              </div>
            </Reveal>

            {filteredTables.length === 0 ? (
              <EmptyState title="Cədvəl tapılmadı" description="Axtarışı dəyişdirin." />
            ) : (
              <motion.div
                variants={reduce ? undefined : staggerList}
                initial={reduce ? false : "hidden"}
                animate="show"
                className="space-y-4"
              >
                {filteredTables.map((table, i) => (
                  <RevealItem key={i}>
                    {/proqnoz|prediction/i.test(table.title) ? (
                      <PredictionsTable table={table} />
                    ) : (
                      <StatsTable table={table} />
                    )}
                  </RevealItem>
                ))}
              </motion.div>
            )}
          </>
        )}
      </div>
    </div>
  );
}
