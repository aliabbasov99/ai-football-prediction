"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import {
  Activity,
  CreditCard,
  Goal,
  Grid3x3,
  Hand,
  Trophy,
} from "lucide-react";
import { STAT_PAGES } from "./constants";
import { cn } from "@/lib/utils";

const ICONS = {
  btts: Hand,
  goals: Goal,
  corner: Grid3x3,
  card: CreditCard,
  other: Activity,
} as const;

export function StatsSidebar() {
  const pathname = usePathname();

  return (
    <aside className="card h-fit overflow-hidden lg:sticky lg:top-20">
      <div className="border-b border-line px-3 py-2.5">
        <p className="text-xs font-semibold uppercase tracking-widerr text-ink-muted">
          Statistika bölmələri
        </p>
      </div>
      <nav className="max-h-[70vh] overflow-y-auto p-1.5">
        {STAT_PAGES.map((page) => {
          const Icon = ICONS[page.icon];
          const active =
            pathname === `/stats/${page.slug}` || pathname === `/footystats/${page.slug}`;
          return (
            <Link
              key={page.slug}
              href={`/footystats/${page.slug}`}
              className={cn(
                "flex items-start gap-2.5 rounded-lg px-2.5 py-2 text-sm transition-colors",
                active ? "bg-surface-3 text-ink" : "text-ink-muted hover:bg-surface-2 hover:text-ink",
              )}
            >
              <Icon className="mt-0.5 h-4 w-4 shrink-0 text-brand" />
              <span className="min-w-0">
                <span className="block font-medium">{page.title}</span>
                <span className="block truncate text-[11px] text-ink-faint">
                  {page.description}
                </span>
              </span>
            </Link>
          );
        })}
      </nav>
    </aside>
  );
}

export function StatPageHeader({
  title,
  description,
  url,
}: {
  title: string;
  description?: string;
  url?: string;
}) {
  return (
    <div className="flex flex-col gap-2 sm:flex-row sm:items-start sm:justify-between">
      <div>
        <h1 className="flex items-center gap-2 text-2xl font-semibold tracking-tight">
          <Trophy className="h-5 w-5 text-brand" />
          {title}
        </h1>
        {description && <p className="mt-1 text-sm text-ink-muted">{description}</p>}
      </div>
      {url && (
        <a
          href={url}
          target="_blank"
          rel="noopener noreferrer"
          className="shrink-0 text-xs text-ink-faint underline-offset-2 hover:text-info hover:underline"
        >
          Mənbəyə aç ↗
        </a>
      )}
    </div>
  );
}
