import type { BetimateStats, FixturePredictions, PredictionItem } from "@/types/football";

/** Matçın unikal açarı — kupon məhsullarını bir-birindən ayırmaq üçün. */
export function matchKey(item: PredictionItem): string {
  return `${item.home_team}|${item.away_team}|${item.date}`;
}

export type OddsSource = "misli" | "betimate" | "oddslot" | "wincomparator" | "sportsgambler" | "footystats";

export interface SourceInfo {
  id: OddsSource;
  label: string;
  has: boolean;
  href?: string;
}

/** Hansı mənbələrin bu matç üçün məlumatı var? */
export function availableSources(predictions: FixturePredictions | null): SourceInfo[] {
  const p = predictions ?? {};
  return [
    { id: "misli", label: "Misli", has: Boolean(p.misli_odds) },
    { id: "betimate", label: "Betimate", has: Boolean(p.betimate_link), href: p.betimate_link },
    { id: "oddslot", label: "Oddslot", has: Boolean(p.oddslot_link || p.oddslot_stats), href: p.oddslot_link },
    {
      id: "wincomparator",
      label: "WinComparator",
      has: Boolean(p.wincomparator_link),
      href: p.wincomparator_link,
    },
    {
      id: "sportsgambler",
      label: "SportsGambler",
      has: Boolean(p.sportsgambler_link),
      href: p.sportsgambler_link,
    },
    {
      id: "footystats",
      label: "FootyStats",
      has: Boolean(p.footystats_h2h_link || p.footystats_stats),
      href: p.footystats_h2h_link,
    },
  ];
}

/** Bir mənbənin hansı bazarları mövcuddur? (sütun başlıqları üçün) */
export function hasMarket(
  predictions: FixturePredictions | null,
  market: "1x2" | "ou25" | "btts" | "dc",
): boolean {
  const p = predictions ?? {};
  const misli = p.misli_odds;
  if (!misli) return false;
  switch (market) {
    case "1x2":
      return Boolean(misli.home_win || misli.draw || misli.away_win);
    case "ou25":
      return Boolean(misli.over_under?.over || misli.over_under?.under);
    case "btts":
      return Boolean(misli.btts?.yes || misli.btts?.no);
    case "dc":
      return Boolean(misli.double_chance?.["1X"]);
  }
}

export function betimateHasOdds(stats?: BetimateStats): boolean {
  if (!stats) return false;
  return Boolean(stats.home_win || stats.draw || stats.away_win);
}

/** Ehtimal sətrində faiz göstərmək üçun: "46.5%" -> 46.5 */
export function percentValue(value: string | number | null | undefined): string {
  if (value === null || value === undefined || value === "") return "—";
  const n = parseFloat(String(value).replace("%", ""));
  return Number.isFinite(n) ? `${n.toFixed(0)}%` : String(value);
}

/** Oyunun keçmiş hissədə bitib-bitmədiyini yoxlamaq üçün sətirləri qruplaşdırır. */
export function groupByLeague(items: PredictionItem[]): Map<string, PredictionItem[]> {
  const map = new Map<string, PredictionItem[]>();
  for (const item of items) {
    const key = item.league_name || "Digər";
    if (!map.has(key)) map.set(key, []);
    map.get(key)!.push(item);
  }
  return map;
}

/** Proqnoz panelində göstərilən bütün bazarları yığır. */
export function marketsOf(item: PredictionItem): string[] {
  const markets: string[] = [];
  const p = item.predictions;
  if (!p) return markets;
  if (hasMarket(p, "1x2")) markets.push("1X2");
  if (hasMarket(p, "dc")) markets.push("Double Chance");
  if (hasMarket(p, "ou25")) markets.push("Over/Under 2.5");
  if (hasMarket(p, "btts")) markets.push("BTTS");
  return markets;
}

/** Matçda heç bir əmsal yoxdursa true — sətri gizlətmək üçün. */
export function hasAnyOdds(predictions: FixturePredictions | null): boolean {
  const p = predictions ?? {};
  return Boolean(
    p.misli_odds ||
      p.betimate_home_win ||
      p.betimate_draw ||
      p.betimate_away_win ||
      p.oddslot_home_chance ||
      p.oddslot_away_chance,
  );
}
