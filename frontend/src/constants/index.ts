/**
 * Əlavə sabitlər. Səhifələr arasında paylaşılır.
 */

/** Kupon məhsullarının maksimum sayı. */
export const MAX_COUPON_ITEMS = 12;

/** PNG ixracının ölçə və keyfiyyəti. */
export const EXPORT_SCALE = 2;
export const EXPORT_BG = "#18181b";

/** Navbar-da göstərilən əsas səhifələr. */
export const NAV_LINKS = [
  { href: "/", label: "Ana səhifə" },
  { href: "/predictions", label: "Proqnozlar" },
  { href: "/schedule", label: "Cədvəl" },
  { href: "/top-bottom", label: "Top / Bottom" },
  { href: "/stats", label: "Statistika" },
  { href: "/footystats", label: "FootyStats" },
] as const;

/** Mobil alt tab bar (Footer.tsx) — 4 əsas keçid. */
export const MOBILE_TABS = [
  { href: "/", label: "Ana" },
  { href: "/predictions", label: "Proqnoz" },
  { href: "/schedule", label: "Cədvəl" },
  { href: "/stats", label: "Stat" },
] as const;

/** Pipeline-i idarə edən addım sırası. */
export const SCRAPE_STEP_ORDER = [
  "footystats_games",
  "footystats_links",
  "footystats_predictions",
  "misli",
  "oddslot",
  "wincomparator_links",
  "wincomparator_predictions",
  "betimate_links",
  "betimate_predictions",
  "sportsgambler_links",
  "sportsgambler_predictions",
] as const;

/** Pipeline statusunu göstərən polling aralığı (ms). */
export const STATUS_POLL_MS = 3000;
