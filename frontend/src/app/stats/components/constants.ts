export interface StatPageMeta {
  slug: string;
  title: string;
  description: string;
  icon: "btts" | "goals" | "corner" | "card" | "other";
}

/**
 * FootyStats stat səhifələri (backend/scripts/scrapeFootyStats.py → STATS_PAGES).
 * Backend boş olsa da siyahı statikdir, ona görə sidebar hər zaman dolu olur.
 */
export const STAT_PAGES: StatPageMeta[] = [
  { slug: "btts-stats", title: "BTTS", description: "İki komanda da qol vurdur?", icon: "btts" },
  { slug: "over15-goals", title: "Over 1.5", description: "1.5-dən çox qol", icon: "goals" },
  { slug: "over25-goals", title: "Over 2.5", description: "2.5-dən çox qol", icon: "goals" },
  { slug: "under25-goals", title: "Under 2.5", description: "2.5-dən az qol", icon: "goals" },
  { slug: "corner-stats", title: "Korner", description: "Korner statistikası", icon: "corner" },
  {
    slug: "1st-2nd-half-goals",
    title: "Yarımlar",
    description: "1-ci və 2-ci yarı qolları",
    icon: "goals",
  },
  {
    slug: "scored-in-both-halves",
    title: "Hər yarıda qol",
    description: "Hər iki yarıda qol vuranlar",
    icon: "goals",
  },
  { slug: "win-draw-win", title: "Qələbə / Heç-heçə", description: "1X2 statistikası", icon: "other" },
  { slug: "referee-stats", title: "Hakim", description: "Hakim statistikası", icon: "other" },
  { slug: "card-stats", title: "Kart", description: "Sarı və qırmızı kart", icon: "card" },
  { slug: "offside-stats", title: "Ofsayt", description: "Ofsayt statistikası", icon: "other" },
  { slug: "clean-sheet-stats", title: "Təmiz oyun", description: "Qol verməyən oyunlar", icon: "other" },
  { slug: "common-score", title: "Tez-tez heç nələr", description: "Ən çox rast gəlinən hesablar", icon: "other" },
  { slug: "shots-on-target", title: "Dəqiq zərbə", description: "Dəqiq zərbə statistikası", icon: "goals" },
  { slug: "draws", title: "Heç-heçələr", description: "Ən çox heç-heçə edən komandalar", icon: "other" },
  { slug: "predictions", title: "Proqnozlar", description: "FootyStats proqnozları", icon: "other" },
];

/** Sütun adlarından rəqəm çıxarmağa çalışan regex. */
export function extractNumber(
  value: string | number | null | undefined,
): number | null {
  if (value === null || value === undefined) return null;
  const n = parseFloat(String(value).replace(/[^\d.,-]/g, "").replace(",", "."));
  return Number.isFinite(n) ? n : null;
}
