"use client";

import { useParams } from "next/navigation";
import { Loader2 } from "lucide-react";
import { useEffect, useState } from "react";
import { StatsSidebar, StatPageHeader } from "@/app/stats/components/StatsSidebar";
import { FilterBar } from "@/app/stats/components/FilterBar";
import { StatsTable } from "@/app/stats/components/StatsTable";
import { PredictionsTable } from "@/app/stats/components/PredictionsTable";
import { STAT_PAGES } from "@/app/stats/components/constants";
import { EmptyState } from "@/components/EmptyState";
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
    <div className="grid gap-5 lg:grid-cols-[260px_1fr]">
      <StatsSidebar />

      <div className="space-y-4">
        <StatPageHeader
          title={page?.page_title ?? meta?.title ?? slug}
          description={meta?.description}
          url={page?.url}
        />

        {loading && (
          <div className="grid place-items-center py-20">
            <Loader2 className="h-6 w-6 animate-spin text-ink-faint" />
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
            <FilterBar value={query} onChange={setQuery} />
            {tables.length === 0 ? (
              <EmptyState title="Cədvəl tapılmadı" description="Axtarışı dəyişdirin." />
            ) : (
              <div className="space-y-4">
                {tables.map((table, i) =>
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
