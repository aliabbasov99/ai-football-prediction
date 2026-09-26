/**
 * Statistika səhifəsinin lokal tipləri.
 */
export type {
  FootyStatsPage,
  FootyStatsPageIndexItem,
  FootyStatsTable,
} from "@/types/football";

/** statistics.tsx daxilində hər səhifə üçün statik meta. */
export interface StatPageMeta {
  slug: string;
  title: string;
  description: string;
  icon: "btts" | "goals" | "corner" | "card" | "other";
}

/** PercentBar tonları. */
export type BarTone = "info" | "success" | "warn" | "danger";
