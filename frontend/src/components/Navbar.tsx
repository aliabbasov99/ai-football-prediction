"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { AnimatePresence, motion, useReducedMotion } from "framer-motion";
import {
  CalendarClock,
  Goal,
  Layers,
  ListOrdered,
  LogIn,
  LogOut,
  Menu,
  Radar,
  ShieldCheck,
  Sigma,
  Ticket,
  TrendingUp,
  UserRound,
  X,
} from "lucide-react";
import { useEffect, useState } from "react";
import { useCoupon } from "@/context/CouponContext";
import { NAV_LINKS } from "@/constants";
import { useAuth } from "@/lib/useAuth";
import { cn } from "@/lib/utils";
import { DUR, EASE_OUT } from "@/components/motion";

/**
 * Hər marşrut üçün KONTEKSTƏ UYĞUN və bir-birindən FƏRQLİ ikon.
 * Əvvəl 3 səhifə `BarChart3` paylaşırdı — istifadəçi "hansı bu?" deyə bilmirdi.
 */
const NAV_ICONS: Record<string, typeof Radar> = {
  "/": Radar, // canlı ümumi vəziyyət — "radar"
  "/predictions": TrendingUp, // proqnoz axını
  "/schedule": CalendarClock, // günlər üzrə cədvəl
  "/top-bottom": ListOrdered, // sıralanmış cədvəl (top/bottom)
  "/stats": Sigma, // rəqəmsal statistika
  "/footystats": Layers, // çoxqatlı detail məlumat
  "/admin": ShieldCheck, // idarəetmə paneli
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
  const { isAdmin, nickname, refresh, logout } = useAuth();
  const reduce = useReducedMotion();

  // Səhifə dəyişəndə rolu yenidən yoxla (giriş / çıxış dəyişikliyi)
  useEffect(() => {
    refresh();
  }, [pathname, refresh]);

  const links: NavItem[] = isAdmin
    ? [...NAV, { href: "/admin", label: "Admin" }]
    : NAV;

  const isActive = (href: string) =>
    href === "/" ? pathname === "/" : pathname.startsWith(href);

  return (
    <header className="sticky top-0 z-40 border-b border-line bg-base/85 backdrop-blur-md">
      <div className="mx-auto flex h-14 max-w-[1600px] items-center gap-3 px-4">
        <Link
          href="/"
          className="group flex items-center gap-2.5 transition-opacity hover:opacity-80"
        >
          <motion.span
            whileHover={reduce ? undefined : { scale: 1.05, rotate: -4 }}
            whileTap={reduce ? undefined : { scale: 0.94 }}
            transition={{ duration: DUR.fast, ease: EASE_OUT }}
            className="grid h-8 w-8 place-items-center rounded-lg bg-brand text-base"
          >
            <Goal className="h-4.5 w-4.5" strokeWidth={2.25} />
          </motion.span>
          <span className="hidden text-[15px] font-semibold tracking-tight text-ink sm:inline">
            AI Football
          </span>
        </Link>

        <nav className="ml-4 hidden items-center gap-1 lg:flex">
          {links.map((item) => {
            const active = isActive(item.href);
            const Icon = NAV_ICONS[item.href] ?? Radar;
            return (
              <Link
                key={item.href}
                href={item.href}
                aria-current={active ? "page" : undefined}
                className={cn(
                  "relative flex items-center gap-1.5 rounded-lg px-3 py-1.5 text-sm font-medium transition-colors duration-150",
                  active
                    ? "text-ink"
                    : "text-ink-muted hover:bg-surface-2 hover:text-ink",
                )}
              >
                {/* Aktiv vəziyyət göstəricisi — 2px zümrüd xət, yoxsa kükürd */}
                {active && (
                  <motion.span
                    layoutId="nav-active"
                    className="absolute inset-x-2 -bottom-[9px] h-0.5 rounded-full bg-brand"
                    transition={{ duration: DUR.base, ease: EASE_OUT }}
                  />
                )}
                <Icon
                  className={cn(
                    "h-3.5 w-3.5 transition-colors duration-150",
                    active ? "text-brand" : "text-ink-faint",
                  )}
                  strokeWidth={2.25}
                />
                {item.label}
              </Link>
            );
          })}
        </nav>

        <div className="ml-auto flex items-center gap-2">
          {isAdmin && (
            <span
              className="pill badge-brand hidden md:inline-flex"
              title={`Admin: ${nickname}`}
            >
              <UserRound className="h-3 w-3" strokeWidth={2.5} />
              {nickname}
            </span>
          )}

          <motion.button
            onClick={open}
            whileHover={reduce ? undefined : { scale: 1.02 }}
            whileTap={reduce ? undefined : { scale: 0.97 }}
            transition={{ duration: DUR.fast, ease: EASE_OUT }}
            className="btn btn-primary"
          >
            <Ticket className="h-4 w-4" strokeWidth={2.25} />
            <span className="hidden sm:inline">Kupon</span>
            {items.length > 0 && (
              <span className="grid h-5 min-w-5 place-items-center rounded-full bg-base/25 px-1 text-xs font-semibold tabular-nums">
                {items.length}
              </span>
            )}
          </motion.button>

          {isAdmin && (
            <button
              onClick={logout}
              title="Çıxış"
              className="btn btn-ghost !px-2.5"
            >
              <LogOut className="h-4 w-4" strokeWidth={2.25} />
              <span className="sr-only">Çıxış</span>
            </button>
          )}

          <button
            onClick={() => setMobileOpen((v) => !v)}
            className="btn btn-ghost !px-2.5 lg:hidden"
            aria-label="Menyu"
            aria-expanded={mobileOpen}
          >
            {mobileOpen ? (
              <X className="h-4.5 w-4.5" strokeWidth={2.25} />
            ) : (
              <Menu className="h-4.5 w-4.5" strokeWidth={2.25} />
            )}
          </button>
        </div>
      </div>

      <AnimatePresence initial={false}>
        {mobileOpen && (
          <motion.nav
            key="mobile-nav"
            initial={reduce ? false : { height: 0, opacity: 0 }}
            animate={{ height: "auto", opacity: 1 }}
            exit={reduce ? undefined : { height: 0, opacity: 0 }}
            transition={{ duration: DUR.base, ease: EASE_OUT }}
            className="overflow-hidden border-t border-line bg-surface/95 backdrop-blur-md lg:hidden"
          >
            <div className="mx-auto grid max-w-[1600px] gap-1 p-3">
              {links.map((item) => {
                const Icon = NAV_ICONS[item.href] ?? Radar;
                const active = isActive(item.href);
                return (
                  <Link
                    key={item.href}
                    href={item.href}
                    onClick={() => setMobileOpen(false)}
                    className={cn(
                      "flex items-center gap-3 rounded-lg px-3 py-2.5 text-sm font-medium transition-colors duration-150",
                      active
                        ? "bg-surface-2 text-ink"
                        : "text-ink-muted hover:bg-surface-2 hover:text-ink",
                    )}
                  >
                    <Icon
                      className={cn(
                        "h-4 w-4 shrink-0",
                        active ? "text-brand" : "text-ink-faint",
                      )}
                      strokeWidth={2.25}
                    />
                    {item.label}
                    {active && (
                      <span className="ml-auto h-1.5 w-1.5 rounded-full bg-brand" />
                    )}
                  </Link>
                );
              })}

              {isAdmin && (
                <button
                  onClick={logout}
                  className="mt-2 flex items-center gap-3 border-t border-line px-3 pt-3 text-sm font-medium text-ink-muted"
                >
                  <LogIn className="h-4 w-4 text-ink-faint" strokeWidth={2.25} />
                  Çıxış ({nickname})
                </button>
              )}
            </div>
          </motion.nav>
        )}
      </AnimatePresence>
    </header>
  );
}
