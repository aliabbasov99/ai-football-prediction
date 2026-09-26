/**
 * Proqnoz səhifəsinin lokal tipləri.
 * Əsas məlumat mənbəyi @/types/football-dir; burada yalnız
 * bu səhifəyə xas tiplər təkrarlanır.
 */
export type {
  BetimateStats,
  BetimateUpcoming,
  FixturePredictions,
  MisliOdds,
  PredictionItem,
  TopScorer,
  UpcomingMatch,
  WinComparatorStats,
} from "@/types/football";

/** Səhifədə göstərilən bazar açarları. */
export type MarketKey = "1x2" | "dc" | "ou25" | "btts";

/** Mənbə növləri — sətır başındakı badicələr. */
export type SourceId =
  | "misli"
  | "betimate"
  | "oddslot"
  | "wincomparator"
  | "sportsgambler"
  | "footystats";

export interface MarketOption {
  key: MarketKey;
  label: string;
  /** OddsHeader-də göstərilən sütun başlığı */
  column: string;
}

export const MARKET_OPTIONS: MarketOption[] = [
  { key: "1x2", label: "1X2", column: "1X2" },
  { key: "dc", label: "Double Chance", column: "DC" },
  { key: "ou25", label: "Over/Under 2.5", column: "O/U 2.5" },
  { key: "btts", label: "BTTS", column: "BTTS" },
];
