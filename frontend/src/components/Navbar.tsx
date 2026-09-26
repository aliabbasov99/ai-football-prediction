"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import {
  Activity,
  BarChart3,
  CalendarDays,
  Menu,
  Shield,
  Ticket,
  TrendingUp,
  X,
} from "lucide-react";
import { useEffect, useState } from "react";
import { useCoupon } from "@/context/CouponContext";
import { NAV_LINKS } from "@/constants";
import { useAuth } from "@/lib/useAuth";
import { cn } from "@/lib/utils";

const NAV_ICONS: Record<string, typeof Activity> = {
  "/": Activity,
  "/predictions": TrendingUp,
  "/schedule": CalendarDays,
  "/top-bottom": BarChart3,
  "/stats": BarChart3,
  "/footystats": BarChart3,
  "/admin": Shield,
};

/** NAV_LINKS `as const` ilə daralır — admin linki üçün geniş tipləyirik. */
interface NavItem {
  href: string;
  label: string;
}

const NAV: NavItem[] = NAV_LINKS.map((l) => ({ href: l.href, label: l.label }));

export function Navbar() {
  const pathname = usePathname();
  const { items, open } = useCoupon();
  const [mobileOpen, setMobileOpen] = useState(false);
  const { isAdmin, refresh } = useAuth();

  // Səhifə dəyişəndə rolu yenidən yoxla (giriş / çıxış dəyişikliyi)
  useEffect(() => {
    refresh();
  }, [pathname, refresh]);

  const links: NavItem[] = isAdmin
    ? [...NAV, { href: "/admin", label: "Admin" }]
    : NAV;

  return (
    <header className="sticky top-0 z-40 border-b border-line bg-base/85 backdrop-blur-md">
      <div className="mx-auto flex h-14 max-w-[1600px] items-center gap-3 px-4">
        <Link href="/" className="flex items-center gap-2 font-bold tracking-tight">
          <span className="grid h-8 w-8 place-items-center rounded-lg bg-brand text-base">
            ⚽
          </span>
          <span className="hidden sm:inline">AI Football</span>
        </Link>

        <nav className="ml-4 hidden items-center gap-1 lg:flex">
          {links.map((item) => {
            const active = item.href === "/" ? pathname === "/" : pathname.startsWith(item.href);
            return (
              <Link
                key={item.href}
                href={item.href}
                className={cn(
                  "rounded-lg px-3 py-1.5 text-sm font-medium transition-colors",
                  active
                    ? "bg-surface-3 text-ink"
                    : "text-ink-muted hover:bg-surface-2 hover:text-ink",
                )}
              >
                {item.label}
              </Link>
            );
          })}
        </nav>

        <div className="ml-auto flex items-center gap-2">
          <button
            onClick={open}
            className="relative inline-flex items-center gap-2 rounded-lg bg-brand px-3 py-1.5 text-sm font-semibold text-white transition-opacity hover:opacity-90"
          >
            <Ticket className="h-4 w-4" />
            <span className="hidden sm:inline">Kupon</span>
            {items.length > 0 && (
              <span className="grid h-5 min-w-5 place-items-center rounded-full bg-white/25 px-1 text-xs font-bold">
                {items.length}
              </span>
            )}
          </button>

          <button
            onClick={() => setMobileOpen((v) => !v)}
            className="grid h-9 w-9 place-items-center rounded-lg border border-line text-ink-muted lg:hidden"
            aria-label="Menyu"
          >
            {mobileOpen ? <X className="h-5 w-5" /> : <Menu className="h-5 w-5" />}
          </button>
        </div>
      </div>

      {mobileOpen && (
        <nav className="border-t border-line bg-surface lg:hidden">
          <div className="mx-auto grid max-w-[1600px] gap-1 p-3">
            {links.map((item) => {
              const Icon = NAV_ICONS[item.href] ?? Activity;
              const active =
                item.href === "/" ? pathname === "/" : pathname.startsWith(item.href);
              return (
                <Link
                  key={item.href}
                  href={item.href}
                  onClick={() => setMobileOpen(false)}
                  className={cn(
                    "flex items-center gap-3 rounded-lg px-3 py-2.5 text-sm font-medium",
                    active ? "bg-surface-3 text-ink" : "text-ink-muted",
                  )}
                >
                  <Icon className="h-4 w-4" />
                  {item.label}
                </Link>
              );
            })}
          </div>
        </nav>
      )}
    </header>
  );
}
