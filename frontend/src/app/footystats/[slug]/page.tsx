"use client";

import { useParams } from "next/navigation";
import { motion, useReducedMotion } from "framer-motion";
import { Loader2 } from "lucide-react";
import { useEffect, useState } from "react";
import { StatsSidebar, StatPageHeader } from "@/app/stats/components/StatsSidebar";
import { FilterBar } from "@/app/stats/components/FilterBar";
import { StatsTable } from "@/app/stats/components/StatsTable";
import { PredictionsTable } from "@/app/stats/components/PredictionsTable";
import { STAT_PAGES } from "@/app/stats/components/constants";
import { EmptyState } from "@/components/EmptyState";
import { Reveal, RevealItem, staggerList } from "@/components/motion";
import { api } from "@/lib/api";
import type { FootyStatsPage } from "@/types/football";

export default function FootyStatsSlugPage() {
  const params = useParams<{ slug: string }>();
  const slug = params.slug;

  // Nəticə slug-ı ilə birgə saxlanılır: yeni slug seçilən kimi əvvəlki
  // səhifə "köhnə" işarələnir və loading göstərilir (stale məlumat yoxdur).
  const [result, setResult] = useState<{
    slug: string;
    page: FootyStatsPage | null;
  } | null>(null);
  const [query, setQuery] = useState("");
  const reduce = useReducedMotion();

  useEffect(() => {
    let cancelled = false;
    api
      .footystatsPage(slug)
      .then((data) => {
        if (!cancelled) setResult({ slug, page: data });
      })
      .catch(() => {
        // Səhifə yoxdur → `page: null` "not found" deməkdir
        if (!cancelled) setResult({ slug, page: null });
      });
    return () => {
      cancelled = true;
    };
  }, [slug]);

  const fresh = result?.slug === slug;
  const page = fresh ? result.page : null;
  const loading = !fresh;
  const notFound = fresh && result.page === null;

  const meta = STAT_PAGES.find((p) => p.slug === slug);

  const tables = (page?.tables ?? []).filter((table) => {
    const q = query.trim().toLowerCase();
    if (!q) return true;
    return table.rows.some((row) => row.some((c) => c && String(c).toLowerCase().includes(q)));
  });

  return (
    <div className="grid gap-6 lg:grid-cols-[260px_1fr]">
      <Reveal>
        <StatsSidebar />
      </Reveal>

      <div className="space-y-6">
        <Reveal>
          <StatPageHeader
            title={page?.page_title ?? meta?.title ?? slug}
            description={meta?.description}
            url={page?.url}
          />
        </Reveal>

        {loading && (
          <div className="grid place-items-center py-20">
            <Loader2 className="h-6 w-6 animate-spin text-ink-faint" strokeWidth={2.25} />
          </div>
        )}

        {!loading && notFound && (
          <EmptyState
            title="Səhifə tapılmadı"
            description={`"${slug}" səhifəsi bazada yoxdur. Pipeline işə salındıqdan sonra burada görünəcək.`}
          />
        )}

        {!loading && page && (
          <>
            <Reveal delay={0.05}>
              <FilterBar value={query} onChange={setQuery} />
            </Reveal>
            {tables.length === 0 ? (
              <EmptyState title="Cədvəl tapılmadı" description="Axtarışı dəyişdirin." />
            ) : (
              <motion.div
                variants={reduce ? undefined : staggerList}
                initial={reduce ? false : "hidden"}
                animate="show"
                className="space-y-4"
              >
                {tables.map((table, i) => (
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
