"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import {
  Activity,
  BarChart3,
  CalendarDays,
  Home,
  Shield,
  TrendingUp,
} from "lucide-react";
import { MOBILE_TABS } from "@/constants";
import { cn } from "@/lib/utils";

const MOBILE_ICONS = {
  "/": Home,
  "/predictions": TrendingUp,
  "/schedule": CalendarDays,
  "/stats": BarChart3,
} as const;

export function Footer() {
  const pathname = usePathname();

  return (
    <footer className="mt-auto border-t border-line bg-surface">
      <div className="mx-auto max-w-[1600px] px-4 py-8 pb-24 lg:pb-8">
        <div className="flex flex-col gap-6 sm:flex-row sm:items-start sm:justify-between">
          <div className="max-w-sm">
            <div className="flex items-center gap-2 font-bold">
              <span className="grid h-7 w-7 place-items-center rounded-lg bg-brand text-sm">
                ⚽
              </span>
              AI Football Prediction
            </div>
            <p className="mt-2 text-xs leading-relaxed text-ink-faint">
              7+ mənbədən əmsal və proqnoz məlumatlarını toplayan analitik platforma.
              Yalnız təhsil və araşdırma məqsədi ilə hazırlanıb.
            </p>
          </div>

          <nav className="grid grid-cols-2 gap-x-10 gap-y-2 text-sm sm:grid-cols-3">
            <Link
              href="/predictions"
              className="flex items-center gap-2 text-ink-muted hover:text-ink"
            >
              <TrendingUp className="h-4 w-4" /> Proqnozlar
            </Link>
            <Link
              href="/schedule"
              className="flex items-center gap-2 text-ink-muted hover:text-ink"
            >
              <CalendarDays className="h-4 w-4" /> Cədvəl
            </Link>
            <Link
              href="/stats"
              className="flex items-center gap-2 text-ink-muted hover:text-ink"
            >
              <BarChart3 className="h-4 w-4" /> Statistika
            </Link>
            <Link
              href="/top-bottom"
              className="flex items-center gap-2 text-ink-muted hover:text-ink"
            >
              <Activity className="h-4 w-4" /> Top / Bottom
            </Link>
            <Link
              href="/footystats"
              className="flex items-center gap-2 text-ink-muted hover:text-ink"
            >
              <BarChart3 className="h-4 w-4" /> FootyStats
            </Link>
            <Link
              href="/admin"
              className="flex items-center gap-2 text-ink-faint hover:text-ink"
            >
              <Shield className="h-4 w-4" /> Admin
            </Link>
          </nav>
        </div>

        <p className="mt-6 border-t border-line-soft pt-4 text-xs text-ink-faint">
          © {new Date().getFullYear()} — Məlumatlar ictimai mənbələrdən toplanır. Məşhur
          pul oyunlarına cavabdehliq daşımır.
        </p>
      </div>

      {/* Mobil alt tab bar — yalnız kiçik ekranlarda görünür */}
      <nav className="fixed inset-x-0 bottom-0 z-30 border-t border-line bg-surface/95 backdrop-blur-md lg:hidden">
        <div className="grid grid-cols-4">
          {MOBILE_TABS.map((tab) => {
            const Icon = MOBILE_ICONS[tab.href as keyof typeof MOBILE_ICONS];
            const active = pathname === tab.href;
            return (
              <Link
                key={tab.href}
                href={tab.href}
                className={cn(
                  "flex flex-col items-center gap-0.5 py-2.5 text-[10px] font-medium transition-colors",
                  active ? "text-brand" : "text-ink-faint",
                )}
              >
                <Icon className="h-5 w-5" />
                {tab.label}
              </Link>
            );
          })}
        </div>
      </nav>
    </footer>
  );
}
