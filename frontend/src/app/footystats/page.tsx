"use client";

import Link from "next/link";
import { motion, useReducedMotion } from "framer-motion";
import { ArrowRight, CircleCheck, CircleDashed, Database, Layers, Loader2 } from "lucide-react";
import { useEffect, useState } from "react";
import { EmptyState } from "@/components/EmptyState";
import { Reveal, RevealItem, staggerList } from "@/components/motion";
import { cn } from "@/lib/utils";
import { api } from "@/lib/api";
import type { FootyStatsPageIndexItem } from "@/types/football";
import { STAT_PAGES } from "@/app/stats/components/constants";

export default function FootyStatsIndexPage() {
  const [items, setItems] = useState<FootyStatsPageIndexItem[]>([]);
  const [loading, setLoading] = useState(true);
  const reduce = useReducedMotion();

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
    <div className="space-y-6">
      <Reveal>
        <div>
          <h1 className="flex items-center gap-2 text-2xl font-semibold tracking-tight">
            <Layers className="h-5.5 w-5.5 text-brand" strokeWidth={2.25} />
            FootyStats
          </h1>
          <p className="mt-1 text-sm text-ink-muted">
            16 statistika kateqoriyası — BTTS, qol, korner, kart, hakim və proqnozlar.
          </p>
        </div>
      </Reveal>

      {loading && (
        <div className="grid place-items-center py-20">
          <Loader2 className="h-6 w-6 animate-spin text-ink-faint" strokeWidth={2.25} />
        </div>
      )}

      {!loading && (
        <motion.div
          variants={reduce ? undefined : staggerList}
          initial={reduce ? false : "hidden"}
          animate="show"
          className="grid gap-3 sm:grid-cols-2 lg:grid-cols-3"
        >
          {STAT_PAGES.map((meta) => {
            const isLoaded = available.has(meta.slug);
            return (
              <RevealItem key={meta.slug}>
                <Link
                  href={`/footystats/${meta.slug}`}
                  className="card card-hover group flex h-full flex-col gap-1.5 p-4 transition-transform duration-150 hover:-translate-y-0.5"
                >
                  <div className="flex items-start justify-between gap-2">
                    <span className="font-semibold text-ink">{meta.title}</span>
                    <ArrowRight
                      className="h-4 w-4 shrink-0 text-ink-faint transition-transform duration-150 group-hover:translate-x-0.5 group-hover:text-brand"
                      strokeWidth={2.25}
                    />
                  </div>
                  <p className="text-xs leading-relaxed text-ink-faint">
                    {meta.description}
                  </p>
                  <span className={cn("pill mt-1.5 w-fit", isLoaded ? "badge-ok" : "badge-muted")}>
                    {isLoaded ? (
                      <CircleCheck className="h-2.5 w-2.5" strokeWidth={2.5} />
                    ) : (
                      <CircleDashed className="h-2.5 w-2.5" strokeWidth={2.25} />
                    )}
                    {isLoaded ? "Məlumat var" : "Məlumat yoxdur"}
                  </span>
                </Link>
              </RevealItem>
            );
          })}
        </motion.div>
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
