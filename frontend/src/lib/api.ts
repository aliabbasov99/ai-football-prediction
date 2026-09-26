/**
 * API istifadəçisi. Next.js rewrites `/api/*` → `http://127.0.0.1:7999/api/*`
 * (next.config.ts) — ona görə hər yerdə nisbi `/api` yolu işlədilir.
 *
 * Token varsa avtomatik əlavə olunur. Backend admin endpoint-ləri `require_admin`
 * istifadə edir, amma frontend giriş məcbur etmir — token yoxdursa 401 qaytarılır.
 */
import type {
  AdminTeam,
  AuthUser,
  FootyStatsPage,
  FootyStatsPageIndexItem,
  FsStatsPipelineState,
  League,
  LeagueConfig,
  Match,
  PipelineState,
  PredictionItem,
  ScrapeToggles,
  TeamXGStats,
  TopBottomMatch,
  TopBottomTeams,
} from "@/types/football";

const TOKEN_KEY = "afp_token";

export function getToken(): string | null {
  if (typeof window === "undefined") return null;
  return window.localStorage.getItem(TOKEN_KEY);
}

export function setToken(token: string | null) {
  if (typeof window === "undefined") return;
  if (token) window.localStorage.setItem(TOKEN_KEY, token);
  else window.localStorage.removeItem(TOKEN_KEY);
}

export class ApiError extends Error {
  constructor(
    public status: number,
    message: string,
  ) {
    super(message);
    this.name = "ApiError";
  }
}

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const token = getToken();
  const headers = new Headers(init?.headers);
  if (!headers.has("Content-Type") && init?.body) {
    headers.set("Content-Type", "application/json");
  }
  if (token) headers.set("Authorization", `Bearer ${token}`);

  const res = await fetch(`/api${path}`, { ...init, headers });

  if (!res.ok) {
    let detail = `HTTP ${res.status}`;
    try {
      const body = await res.json();
      if (body?.detail) detail = String(body.detail);
    } catch {
      /* JSON deyil — HTTP kodu saxlanılır */
    }
    throw new ApiError(res.status, detail);
  }

  if (res.status === 204) return undefined as T;
  return (await res.json()) as T;
}

/* ── Public ── */

export const api = {
  health: () => request<{ status: string; message: string }>("/health"),

  leagues: () => request<League[]>("/leagues"),

  leagueTeams: (leagueId: string) => request<TeamXGStats[]>(`/leagues/${leagueId}/teams`),

  team: (teamId: string) => request<TeamXGStats>(`/teams/${teamId}`),

  predictions: () => request<PredictionItem[]>("/predictions"),

  liveMatches: () => request<Match[]>("/matches/live"),

  topBottomTeams: () => request<TopBottomTeams>("/top-bottom/teams"),

  topBottomMatches: (limit = 100) =>
    request<TopBottomMatch[]>(`/top-bottom/matches?limit=${limit}`),

  footystatsPages: () => request<FootyStatsPageIndexItem[]>("/footystats/pages"),

  footystatsPage: (slug: string) => request<FootyStatsPage>(`/footystats/page/${slug}`),

  /* ── Auth (opsional — giriş məcbur deyil) ── */

  login: (nickname: string, password: string) =>
    request<{ access_token: string; token_type: string; user: AuthUser }>("/auth/login", {
      method: "POST",
      body: JSON.stringify({ nickname, password }),
    }),

  me: () => request<{ user: AuthUser }>("/auth/me"),

  users: () => request<{ users: AuthUser[] }>("/auth/users"),

  /* ── Admin (token tələb edir) ── */

  adminStatus: () => request<PipelineState>("/admin/status-live"),

  adminStatusStatic: () => request<PipelineState>("/admin/status"),

  adminScrapeStart: (toggles: ScrapeToggles) =>
    request<{ status: string; message?: string }>("/admin/scrape-start", {
      method: "POST",
      body: JSON.stringify(toggles),
    }),

  adminClearDb: () =>
    request<{ status: string; message?: string }>("/admin/clear-db", { method: "POST" }),

  adminLeagues: () => request<{ leagues: LeagueConfig[] }>("/admin/leagues"),

  adminCreateLeague: (data: Partial<LeagueConfig>) =>
    request<{ status: string }>("/admin/leagues", {
      method: "POST",
      body: JSON.stringify(data),
    }),

  adminUpdateLeague: (id: string, data: Partial<LeagueConfig>) =>
    request<{ status: string }>(`/admin/leagues/${id}`, {
      method: "PUT",
      body: JSON.stringify(data),
    }),

  adminDeleteLeague: (id: string) =>
    request<{ status: string }>(`/admin/leagues/${id}`, { method: "DELETE" }),

  adminTeams: (leagueId: string) =>
    request<{ teams: AdminTeam[] }>(`/admin/teams?league_id=${encodeURIComponent(leagueId)}`),

  adminCreateTeam: (data: Partial<AdminTeam>) =>
    request<{ status: string }>("/admin/teams", {
      method: "POST",
      body: JSON.stringify(data),
    }),

  adminUpdateTeam: (id: string, data: Partial<AdminTeam>) =>
    request<{ status: string }>(`/admin/teams/${id}`, {
      method: "PUT",
      body: JSON.stringify(data),
    }),

  adminDeleteTeam: (id: string) =>
    request<{ status: string }>(`/admin/teams/${id}`, { method: "DELETE" }),

  adminSyncTeams: (leagueId: string) =>
    request<{ status: string; synced: number }>("/admin/teams/sync", {
      method: "POST",
      body: JSON.stringify({ league_id: leagueId }),
    }),

  adminBulkUpdateTeams: (
    leagueId: string,
    payload: { aliases?: Record<string, string[]>; logos?: Record<string, string> },
  ) =>
    request<{
      status: string;
      aliases_updated: number;
      logos_updated: number;
      not_found: string[];
    }>("/admin/teams/bulk-update", {
      method: "POST",
      body: JSON.stringify({ league_id: leagueId, ...payload }),
    }),

  adminScrapeFootystatsGames: () =>
    request<{ status: string; message?: string }>("/admin/scrape-footystats-games", {
      method: "POST",
    }),

  adminScrapeFootystatsStats: () =>
    request<{ status: string; message?: string }>("/admin/scrape-footystats-stats", {
      method: "POST",
    }),

  adminFootystatsStatsStatus: () =>
    request<FsStatsPipelineState>("/admin/scrape-footystats-stats/status"),
};
