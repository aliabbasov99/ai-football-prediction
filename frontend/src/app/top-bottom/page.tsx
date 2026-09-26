"use client";

import { motion, useReducedMotion } from "framer-motion";
import { GitCompareArrows, Loader2, Swords, TrendingDown, TrendingUp } from "lucide-react";
import { useEffect, useState } from "react";
import {
  TopBottomMatchRow,
  TopBottomTeamCard,
} from "./components/TopBottomCards";
import { EmptyState } from "@/components/EmptyState";
import { Reveal, RevealItem, staggerList } from "@/components/motion";
import { api } from "@/lib/api";
import type { TopBottomMatch, TopBottomTeams } from "@/types/football";

export default function TopBottomPage() {
  const [teams, setTeams] = useState<TopBottomTeams | null>(null);
  const [matches, setMatches] = useState<TopBottomMatch[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const reduce = useReducedMotion();

  useEffect(() => {
    Promise.all([api.topBottomTeams(), api.topBottomMatches(50)])
      .then(([t, m]) => {
        setTeams(t);
        setMatches(m);
      })
      .catch((e) => setError(e.message))
      .finally(() => setLoading(false));
  }, []);

  return (
    <div className="space-y-6">
      <Reveal>
        <div>
          <h1 className="flex items-center gap-2 text-2xl font-semibold tracking-tight">
            <GitCompareArrows className="h-5.5 w-5.5 text-brand" strokeWidth={2.25} />
            Top vs Bottom
          </h1>
          <p className="mt-1 text-sm text-ink-muted">
            Cədvəlin yuxarı və aşağı hissəsindəki komandaların qarşılaşmaları.
          </p>
        </div>
      </Reveal>

      {loading && (
        <div className="grid place-items-center py-20">
          <Loader2 className="h-6 w-6 animate-spin text-ink-faint" strokeWidth={2.25} />
        </div>
      )}

      {error && !loading && <EmptyState title="Məlumat yüklənmədi" description={error} />}

      {!loading && !error && (
        <>
          <div className="grid gap-6 lg:grid-cols-2">
            <Reveal delay={0.05}>
              <section className="space-y-3">
                <h2 className="flex items-center gap-2 text-sm font-semibold uppercase tracking-wider text-ink">
                  <TrendingUp className="h-4 w-4 text-success" strokeWidth={2.25} />
                  Top komandalar
                </h2>
                {teams?.top_teams?.length ? (
                  <motion.div
                    variants={reduce ? undefined : staggerList}
                    initial={reduce ? false : "hidden"}
                    animate="show"
                    className="space-y-2"
                  >
                    {teams.top_teams.map((t, i) => (
                      <RevealItem key={`${t.team_name}-${i}`}>
                        <TopBottomTeamCard team={t} tone="top" />
                      </RevealItem>
                    ))}
                  </motion.div>
                ) : (
                  <EmptyState title="Top komanda yoxdur" />
                )}
              </section>
            </Reveal>

            <Reveal delay={0.1}>
              <section className="space-y-3">
                <h2 className="flex items-center gap-2 text-sm font-semibold uppercase tracking-wider text-ink">
                  <TrendingDown className="h-4 w-4 text-danger" strokeWidth={2.25} />
                  Bottom komandalar
                </h2>
                {teams?.bottom_teams?.length ? (
                  <motion.div
                    variants={reduce ? undefined : staggerList}
                    initial={reduce ? false : "hidden"}
                    animate="show"
                    className="space-y-2"
                  >
                    {teams.bottom_teams.map((t, i) => (
                      <RevealItem key={`${t.team_name}-${i}`}>
                        <TopBottomTeamCard team={t} tone="bottom" />
                      </RevealItem>
                    ))}
                  </motion.div>
                ) : (
                  <EmptyState title="Bottom komanda yoxdur" />
                )}
              </section>
            </Reveal>
          </div>

          <Reveal delay={0.15}>
            <section className="space-y-3">
              <h2 className="flex items-center gap-2 text-sm font-semibold uppercase tracking-wider text-ink">
                <Swords className="h-4 w-4 text-ink-muted" strokeWidth={2.25} />
                Top — Bottom qarşılaşmaları
              </h2>
              {matches.length === 0 ? (
                <EmptyState title="Qarşılaşma tapılmadı" />
              ) : (
                <motion.div
                  variants={reduce ? undefined : staggerList}
                  initial={reduce ? false : "hidden"}
                  animate="show"
                  className="space-y-2"
                >
                  {matches.map((m, i) => (
                    <RevealItem key={`${m.home_team}-${m.away_team}-${i}`}>
                      <TopBottomMatchRow match={m} />
                    </RevealItem>
                  ))}
                </motion.div>
              )}
            </section>
          </Reveal>
        </>
      )}
    </div>
  );
}
