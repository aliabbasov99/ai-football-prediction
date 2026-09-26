/**
 * Backend Pydantic modelləri ilə eyni forma (backend/models.py).
 * Bu fayl frontend-in yegan məlumat mənbəyidir — komponentlər buradan tipləyir.
 */

export interface GameStats {
  games: number;
  xg_for: number;
  xg_against: number;
  goals_for: number;
  goals_against: number;
}

export interface TeamXGStats {
  team_id: string;
  team_name: string;
  team_logo: string;
  position: number;
  points: number;
  won: number;
  drawn: number;
  lost: number;
  goal_difference: string;
  form: string;
  last_30_games: GameStats;
  league_games: GameStats;
  cup_games: GameStats;
}

export interface League {
  id: string;
  name: string;
  country: string;
  logo: string;
}

export interface Last5Game {
  opponent: string;
  opponent_logo: string;
  home_away: string;
  score: string | null;
  xg_for: number;
  xg_against: number;
  date: string;
}

export interface Match {
  id: string;
  home_team: string;
  home_team_id: string;
  home_team_position: number;
  away_team: string;
  away_team_id: string;
  away_team_position: number;
  home_logo: string;
  away_logo: string;
  home_xg: number;
  away_xg: number;
  score: string | null;
  date: string;
  league: string;
  league_name: string;
  home_last5: Last5Game[];
  away_last5: Last5Game[];
}

/* ── /api/predictions ── */

/** misli.az əmsalları (scrape_misli_all.py) */
export interface MisliOdds {
  home_win?: string;
  draw?: string;
  away_win?: string;
  double_chance?: { "1X"?: string; "12"?: string; "X2"?: string };
  over_under?: { under?: string; over?: string };
  btts?: { yes?: string; no?: string };
}

/** betimate (scrape_betimate_details.py) */
export interface BetimateStats {
  home_win?: string;
  draw?: string;
  away_win?: string;
  under_2_5?: string;
  over_2_5?: string;
  btts_yes?: string;
  btts_no?: string;
}

export interface UpcomingMatch {
  date?: string;
  home?: string;
  away?: string;
  score?: string;
  league?: string;
}

export interface TopScorer {
  name?: string;
  team?: string;
  goals?: string | number;
  team_logo?: string;
}

export interface BetimateUpcoming {
  home: UpcomingMatch[];
  away: UpcomingMatch[];
}

/** sportsgambler (scrape_sportsgambler_details.py) */
export interface SportsGamblerStats {
  prediction?: string;
  correct_score?: string;
}

/** wincomparator (scrape_external_details.py) */
export interface WinComparator1X2 {
  outcome?: string;
  prediction?: string;
  probability?: string;
  odds?: string;
}

export interface WinComparatorStats {
  "1x2"?: WinComparator1X2;
  under_over?: { type?: string; line?: string; probability?: string; odds?: string };
  btts?: { type?: string; line?: string; probability?: string; odds?: string };
}

/** oddslot (scrape_external_details.py) */
export interface OddslotStats {
  home_team?: string;
  away_team?: string;
  home_percent?: string;
  away_percent?: string;
  home_odds?: string;
  away_odds?: string;
}

/** footystats H2H — açar söz: {home, away} (scrape_external_details.py) */
export type FootystatsH2H = Record<string, { home: string; away: string }>;

export interface FixturePredictions {
  misli_odds?: MisliOdds | null;

  betimate_link?: string;
  betimate_home_win?: string;
  betimate_draw?: string;
  betimate_away_win?: string;
  betimate_score?: string;
  betimate_stats?: BetimateStats;
  betimate_upcoming?: BetimateUpcoming;

  sportsgambler_link?: string;
  sportsgambler_stats?: SportsGamblerStats;

  wincomparator_link?: string;
  wincomparator_stats?: WinComparatorStats;

  oddslot_link?: string;
  oddslot_home_chance?: string;
  oddslot_away_chance?: string;
  oddslot_stats?: OddslotStats;

  footystats_h2h_link?: string;
  footystats_stats?: FootystatsH2H;

  top_scorers?: TopScorer[];
}

export interface PredictionItem {
  league_name: string;
  home_team: string;
  away_team: string;
  date: string;
  date_az: string;
  time: string;
  time_az: string;
  home_logo: string;
  away_logo: string;
  predictions: FixturePredictions | null;
}

/* ── Top / Bottom ── */

export interface TopBottomTeam {
  team_name?: string;
  team_logo?: string;
  league_name?: string;
  position?: number;
  points?: number;
  team_id?: string;
}

export interface TopBottomTeams {
  top_teams: TopBottomTeam[];
  bottom_teams: TopBottomTeam[];
}

export interface TopBottomMatch {
  home_team: string;
  away_team: string;
  date?: string;
  time?: string;
  league_name?: string;
  home_logo?: string;
  away_logo?: string;
  home_position?: number;
  away_position?: number;
}

/* ── FootyStats səhifələri (scrapeFootyStats.py) ── */

export interface FootyStatsTable {
  title: string;
  headers: string[];
  rows: (string | null)[][];
}

export interface FootyStatsPage {
  page: string;
  page_title: string;
  url: string;
  tables: FootyStatsTable[];
}

export interface FootyStatsPageIndexItem {
  page: string;
  page_title: string;
  url: string;
}

/* ── Admin ── */

export interface ScrapeToggles {
  footystats_games: boolean;
  misli: boolean;
  oddslot: boolean;
  wincomparator_links: boolean;
  wincomparator_predictions: boolean;
  footystats_links: boolean;
  footystats_predictions: boolean;
  betimate_links: boolean;
  betimate_predictions: boolean;
  sportsgambler_links: boolean;
  sportsgambler_predictions: boolean;
}

export interface PipelineState {
  is_running: boolean;
  current_step: string;
  current_step_index: number;
  total_steps: number;
  progress: number;
  step_status: string;
  error: string;
  report: Record<string, unknown> | null;
}

export interface FsStatsPipelineState {
  is_running: boolean;
  progress: number;
  current_page: string;
}

export interface LeagueConfig {
  _id?: string;
  name: string;
  slug?: string;
  country?: string;
  logo?: string;
  enabled?: boolean;
  wincomparator_link?: string;
  betimate_link?: string;
  sportsgambler_link?: string;
  footystats_link?: string;
}

export interface AdminTeam {
  _id: string;
  name: string;
  league_id: string;
  logo: string;
  aliases: string[];
}

export interface AuthUser {
  id: string;
  nickname: string;
  role: string;
  created_at?: string;
}
