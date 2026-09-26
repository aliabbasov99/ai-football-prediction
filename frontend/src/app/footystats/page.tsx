"use client";

import Link from "next/link";
import { ArrowRight, Database, Loader2 } from "lucide-react";
import { useEffect, useState } from "react";
import { EmptyState } from "@/components/EmptyState";
import { api } from "@/lib/api";
import type { FootyStatsPageIndexItem } from "@/types/football";
import { STAT_PAGES } from "@/app/stats/components/constants";

export default function FootyStatsIndexPage() {
  const [items, setItems] = useState<FootyStatsPageIndexItem[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    api
      .footystatsPages()
      .then(setItems)
      .catch(() => setItems([]))
      .finally(() => setLoading(false));
  }, []);

  // Backend boş olsa da statik siyahını göstəririk — hansı səhifələrin
  // mövcud olduğunu istifadəçiyə əvvəlcədən bildiririk.
  const available = new Set(items.map((i) => i.page));

  return (
    <div className="space-y-5">
      <div>
        <h1 className="text-2xl font-bold tracking-tight">FootyStats</h1>
        <p className="mt-1 text-sm text-ink-muted">
          16 statistika kateqoriyası — BTTS, qol, korner, kart, hakim və proqnozlar.
        </p>
      </div>

      {loading && (
        <div className="grid place-items-center py-20">
          <Loader2 className="h-6 w-6 animate-spin text-ink-faint" />
        </div>
      )}

      {!loading && (
        <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
          {STAT_PAGES.map((meta) => {
            const isLoaded = available.has(meta.slug);
            return (
              <Link
                key={meta.slug}
                href={`/footystats/${meta.slug}`}
                className="card card-hover group flex flex-col gap-1 p-3.5"
              >
                <div className="flex items-start justify-between gap-2">
                  <span className="font-semibold text-ink">{meta.title}</span>
                  <ArrowRight className="h-4 w-4 shrink-0 text-ink-faint transition-transform group-hover:translate-x-0.5 group-hover:text-brand" />
                </div>
                <p className="text-xs text-ink-faint">{meta.description}</p>
                <span
                  className={
                    isLoaded
                      ? "mt-1 inline-flex w-fit items-center gap-1 rounded-md bg-success/15 px-1.5 py-0.5 text-[10px] font-semibold text-success"
                      : "mt-1 inline-flex w-fit items-center gap-1 rounded-md bg-surface-2 px-1.5 py-0.5 text-[10px] font-semibold text-ink-faint"
                  }
                >
                  <Database className="h-2.5 w-2.5" />
                  {isLoaded ? "Məlumat var" : "Məlumat yoxdur"}
                </span>
              </Link>
            );
          })}
        </div>
      )}

      {!loading && items.length === 0 && (
        <EmptyState
          icon={Database}
          title="Hələ məlumat yoxdur"
          description="Səhifələr yuxarıda göstərilir, lakin bazada hələ məlumat yoxdur. Admin panelindən FootyStats pipeline-ini işə salın."
        />
      )}
    </div>
  );
}
