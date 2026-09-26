"use client";

/** Kupon məhsulları üçün tiplər — CouponContext ilə paylaşılır. */
export interface CouponSelection {
  /** Unikal açar: `${matchKey}|${marketKey}` */
  key: string;
  matchKey: string;
  marketKey: string;
  /** "1X2", "Over/Under 2.5", "BTTS" və s. — UI-da başlıq kimi */
  marketLabel: string;
  leagueName: string;
  homeTeam: string;
  awayTeam: string;
  homeLogo: string;
  awayLogo: string;
  /** Seçilmiş tərəf: "1" | "X" | "2" | "Over" | "Under" | "Bəli" | "Xeyr" */
  selection: string;
  /** Əmsal (string kimi saxlanılır — "2.15", "1.01" və s.) */
  odds: string;
  date?: string;
  time?: string;
}

const ODDS_KEYS = [
  "home_win",
  "draw",
  "away_win",
  "1X",
  "12",
  "X2",
  "over",
  "under",
  "btts_yes",
  "btts_no",
] as const;

/** "2.15" -> 2.15 ; əmsal yoxdursa 0 (hesablamaya daxil edilmir) */
export function oddsValue(odds: string | number | null | undefined): number {
  if (odds === null || odds === undefined || odds === "") return 0;
  const n = typeof odds === "number" ? odds : parseFloat(String(odds).replace(",", "."));
  return Number.isFinite(n) && n > 1 ? n : 0;
}

/** Bütün məhsulların vurulması */
export function totalOdds(items: CouponSelection[]): number {
  return items.reduce((acc, item) => acc * (oddsValue(item.odds) || 1), 1);
}

export function potentialReturn(items: CouponSelection[], stake: number): number {
  const t = totalOdds(items);
  return t > 0 ? t * stake : 0;
}

/**
 * Eyni matçın iki məhsulunun bir-birini "ləğv etməsi" qarşılıqlı olaraq
 * mümkündürsə sistem kuponuna daxil edilmir (1 və 2 eyni anda).
 */
export function hasConflictingSelections(items: CouponSelection[]): boolean {
  const byMatch = new Map<string, Set<string>>();
  for (const item of items) {
    if (!ODDS_KEYS.includes(item.marketKey as (typeof ODDS_KEYS)[number])) continue;
    if (!byMatch.has(item.matchKey)) byMatch.set(item.matchKey, new Set());
    byMatch.get(item.matchKey)!.add(item.marketKey);
  }
  for (const keys of byMatch.values()) {
    if (keys.has("home_win") && keys.has("away_win")) return true;
    if (keys.has("over") && keys.has("under")) return true;
    if (keys.has("btts_yes") && keys.has("btts_no")) return true;
  }
  return false;
}

/** Escape + satır sonları — kupon PNG ixracında təhlükəli HTML daxil edilməsinin qarşısını alır. */
export function escapeHtml(value: string): string {
  return value
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;")
    .replace(/'/g, "&#39;");
}
