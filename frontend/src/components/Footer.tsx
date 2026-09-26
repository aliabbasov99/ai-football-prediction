"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { motion, useReducedMotion } from "framer-motion";
import {
  CalendarClock,
  Goal,
  GitCompareArrows,
  Layers,
  Radar,
  ShieldCheck,
  Sigma,
  TrendingUp,
} from "lucide-react";
import { MOBILE_TABS } from "@/constants";
import { useAuth } from "@/lib/useAuth";
import { cn } from "@/lib/utils";
import { DUR, EASE_OUT } from "@/components/motion";

/** Navbar ilə eyni ikon xəritəsi — vizual dil bütün layihədə eyni qalsın. */
const LINK_ICONS = {
  "/predictions": TrendingUp,
  "/schedule": CalendarClock,
  "/stats": Sigma,
  "/top-bottom": GitCompareArrows,
  "/footystats": Layers,
  "/admin": ShieldCheck,
} as const;

const MOBILE_ICONS = {
  "/": Radar,
  "/predictions": TrendingUp,
  "/schedule": CalendarClock,
  "/stats": Sigma,
} as const;

export function Footer() {
  const pathname = usePathname();
  const { isAdmin } = useAuth();
  const reduce = useReducedMotion();

  const links = [
    { href: "/predictions", label: "Proqnozlar" },
    { href: "/schedule", label: "Cədvəl" },
    { href: "/stats", label: "Statistika" },
    { href: "/top-bottom", label: "Top / Bottom" },
    { href: "/footystats", label: "FootyStats" },
    // Admin yalnız adminlərə görünür
    ...(isAdmin ? [{ href: "/admin" as const, label: "Admin" }] : []),
  ];

  return (
    <footer className="mt-auto border-t border-line bg-surface/50 backdrop-blur-sm">
      <div className="mx-auto max-w-[1600px] px-4 py-8 pb-24 lg:pb-8">
        <div className="flex flex-col gap-6 sm:flex-row sm:items-start sm:justify-between">
          <div className="max-w-sm">
            <div className="flex items-center gap-2 text-sm font-semibold">
              <span className="grid h-7 w-7 place-items-center rounded-lg bg-brand text-base">
                <Goal className="h-3.5 w-3.5" strokeWidth={2.5} />
              </span>
              AI Football Prediction
            </div>
            <p className="mt-2.5 text-xs leading-relaxed text-ink-faint">
              7+ mənbədən əmsal və proqnoz məlumatlarını toplayan analitik platforma.
              Yalnız təhsil və araşdırma məqsədi ilə hazırlanıb.
            </p>
          </div>

          <nav className="grid grid-cols-2 gap-x-10 gap-y-2.5 text-sm sm:grid-cols-3">
            {links.map((item) => {
              const Icon = LINK_ICONS[item.href as keyof typeof LINK_ICONS];
              return (
                <Link
                  key={item.href}
                  href={item.href}
                  className="group flex items-center gap-2 text-ink-muted transition-colors duration-150 hover:text-ink"
                >
                  {Icon && (
                    <Icon
                      className="h-4 w-4 text-ink-faint transition-colors duration-150 group-hover:text-brand"
                      strokeWidth={2.25}
                    />
                  )}
                  {item.label}
                </Link>
              );
            })}
          </nav>
        </div>

        <p className="mt-6 border-t border-line-soft pt-4 text-xs text-ink-faint">
          © {new Date().getFullYear()} — Məlumatlar ictimai mənbələrdən toplanır. Məşhur
          pul oyunlarına cavabdehlik daşımır.
        </p>
      </div>

      {/* Mobil alt tab bar — yalnız kiçik ekranlarda görünür */}
      <nav className="fixed inset-x-0 bottom-0 z-30 border-t border-line bg-base/90 backdrop-blur-md lg:hidden">
        <div className="grid grid-cols-4">
          {MOBILE_TABS.map((tab) => {
            const Icon = MOBILE_ICONS[tab.href as keyof typeof MOBILE_ICONS];
            const active = pathname === tab.href;
            return (
              <Link
                key={tab.href}
                href={tab.href}
                aria-current={active ? "page" : undefined}
                className={cn(
                  "relative flex flex-col items-center gap-0.5 py-2.5 text-[10px] font-medium transition-colors duration-150",
                  active ? "text-brand" : "text-ink-faint",
                )}
              >
                {active && (
                  <motion.span
                    layoutId="tab-active"
                    className="absolute inset-x-5 top-0 h-0.5 rounded-full bg-brand"
                    transition={{ duration: DUR.base, ease: EASE_OUT }}
                  />
                )}
                <motion.span
                  animate={reduce ? undefined : { y: active ? -1 : 0 }}
                  transition={{ duration: DUR.fast, ease: EASE_OUT }}
                >
                  <Icon className="h-5 w-5" strokeWidth={active ? 2.25 : 2} />
                </motion.span>
                {tab.label}
              </Link>
            );
          })}
        </div>
      </nav>
    </footer>
  );
}
