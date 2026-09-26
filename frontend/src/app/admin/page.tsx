"use client";

import {
  AlertTriangle,
  Database,
  Loader2,
  LogIn,
  Play,
  Shield,
  Trash2,
} from "lucide-react";
import { useCallback, useEffect, useState } from "react";
import { PipelineReport, PipelineStatusCard } from "./components/PipelineReport";
import { ProgressBar } from "./components/ProgressBar";
import { Toggle } from "./components/Toggle";
import { api, ApiError, getToken, setToken } from "@/lib/api";
import { useAuth } from "@/lib/useAuth";
import type { PipelineState, ScrapeToggles } from "@/types/football";

const DEFAULT_TOGGLES: ScrapeToggles = {
  footystats_games: true,
  misli: true,
  oddslot: true,
  wincomparator_links: true,
  wincomparator_predictions: true,
  footystats_links: true,
  footystats_predictions: true,
  betimate_links: true,
  betimate_predictions: true,
  sportsgambler_links: true,
  sportsgambler_predictions: true,
};

const GROUPS: Array<{ title: string; keys: Array<keyof ScrapeToggles> }> = [
  { title: "FootyStats", keys: ["footystats_games", "footystats_links", "footystats_predictions"] },
  { title: "Misli.az", keys: ["misli"] },
  { title: "WinComparator", keys: ["wincomparator_links", "wincomparator_predictions"] },
  { title: "Betimate", keys: ["betimate_links", "betimate_predictions"] },
  { title: "SportsGambler", keys: ["sportsgambler_links", "sportsgambler_predictions"] },
  { title: "Oddslot", keys: ["oddslot"] },
];

const LABELS: Record<keyof ScrapeToggles, string> = {
  footystats_games: "Oyunlar (games)",
  misli: "Əmsallar",
  oddslot: "Faizlər",
  wincomparator_links: "Linklər",
  wincomparator_predictions: "Proqnozlar",
  footystats_links: "Linklər",
  footystats_predictions: "Proqnozlar",
  betimate_links: "Linklər",
  betimate_predictions: "Proqnozlar",
  sportsgambler_links: "Linklər",
  sportsgambler_predictions: "Proqnozlar",
};

export default function AdminPage() {
  const [nickname, setNickname] = useState("");
  const [password, setPassword] = useState("");
  const [authError, setAuthError] = useState<string | null>(null);
  const [authLoading, setAuthLoading] = useState(false);

  const [toggles, setToggles] = useState<ScrapeToggles>(DEFAULT_TOGGLES);
  const [state, setState] = useState<PipelineState | null>(null);
  const [message, setMessage] = useState<{ kind: "ok" | "err"; text: string } | null>(null);
  const [busy, setBusy] = useState(false);

  const { status, isAdmin, nickname: adminName, refresh, logout: logoutAuth } =
    useAuth();

  // status-live SSE deyil, sadə JSON — polling ilə izlənir
  const poll = useCallback(async () => {
    if (!getToken()) return;
    try {
      setState(await api.adminStatus());
    } catch {
      /* sessiya bitə bilər — növbəti cəhddə aşkarlanacaq */
    }
  }, []);

  useEffect(() => {
    if (!isAdmin) return;
    // İlk sorğunu `setInterval` callback-i kimi göndəririk ki, effect
    // gövdəsində birbaşa setState çağrılmasın (React 19 qaydası).
    const first = setTimeout(poll, 0);
    const timer = setInterval(poll, 3000);
    return () => {
      clearTimeout(first);
      clearInterval(timer);
    };
  }, [isAdmin, poll]);

  async function login(e: React.FormEvent) {
    e.preventDefault();
    setAuthLoading(true);
    setAuthError(null);
    try {
      const res = await api.login(nickname, password);
      setToken(res.access_token);
      setPassword("");
      // Rolu `useAuth` yenidən oxusun
      refresh();
    } catch (e) {
      setAuthError(e instanceof ApiError ? e.message : "Giriş uğursuz oldu");
    } finally {
      setAuthLoading(false);
    }
  }

  function logout() {
    setToken(null);
    setState(null);
    logoutAuth();
  }

  async function startPipeline() {
    setBusy(true);
    setMessage(null);
    try {
      const res = await api.adminScrapeStart(toggles);
      setMessage({
        kind: res.status === "warning" ? "err" : "ok",
        text: res.message ?? (res.status === "warning" ? "Pipeline artıq işləyir" : "Pipeline başladı"),
      });
      void poll();
    } catch (e) {
      setMessage({ kind: "err", text: e instanceof ApiError ? e.message : "Xəta baş verdi" });
    } finally {
      setBusy(false);
    }
  }

  async function clearDb() {
    if (!confirm("Bütün məlumat bazaları silinsin? Bu əməliyat geri qaytarıla bilməz.")) return;
    setBusy(true);
    setMessage(null);
    try {
      const res = await api.adminClearDb();
      setMessage({ kind: "ok", text: res.message ?? "Baza təmizləndi" });
      void poll();
    } catch (e) {
      setMessage({ kind: "err", text: e instanceof ApiError ? e.message : "Xəta baş verdi" });
    } finally {
      setBusy(false);
    }
  }

  async function runFootyStats(kind: "games" | "stats") {
    setBusy(true);
    setMessage(null);
    try {
      const res =
        kind === "games"
          ? await api.adminScrapeFootystatsGames()
          : await api.adminScrapeFootystatsStats();
      setMessage({ kind: "ok", text: res.message ?? "Əmr göndərildi" });
    } catch (e) {
      setMessage({ kind: "err", text: e instanceof ApiError ? e.message : "Xəta baş verdi" });
    } finally {
      setBusy(false);
    }
  }

  /* ── Giriş ekranı ── */
  if (status === "loading") {
    return (
      <div className="grid place-items-center py-20">
        <Loader2 className="h-6 w-6 animate-spin text-ink-faint" />
      </div>
    );
  }

  if (!isAdmin) {
    return (
      <div className="mx-auto max-w-sm">
        <div className="card p-6">
          <h1 className="flex items-center gap-2 text-lg font-bold">
            <Shield className="h-5 w-5 text-brand" /> Admin girişi
          </h1>
          <p className="mt-1 text-sm text-ink-muted">
            Bu səhifə yalnız administrator üçün. Admin hesabı ilə daxil olun.
          </p>

          <form onSubmit={login} className="mt-5 space-y-3">
            <input
              value={nickname}
              onChange={(e) => setNickname(e.target.value)}
              placeholder="İstifadəçi adı"
              autoComplete="username"
              className="w-full rounded-lg border border-line bg-surface-2 px-3 py-2 text-sm text-ink outline-none focus:border-brand"
            />
            <input
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              placeholder="Şifrə"
              autoComplete="current-password"
              className="w-full rounded-lg border border-line bg-surface-2 px-3 py-2 text-sm text-ink outline-none focus:border-brand"
            />

            {authError && (
              <p className="flex items-center gap-1.5 text-xs text-danger">
                <AlertTriangle className="h-3.5 w-3.5" />
                {authError}
              </p>
            )}

            <button
              type="submit"
              disabled={authLoading}
              className="inline-flex w-full items-center justify-center gap-2 rounded-lg bg-brand px-3 py-2 text-sm font-semibold text-white transition-opacity hover:opacity-90 disabled:opacity-50"
            >
              {authLoading ? <Loader2 className="h-4 w-4 animate-spin" /> : <LogIn className="h-4 w-4" />}
              Daxil ol
            </button>
          </form>
        </div>
      </div>
    );
  }

  /* ── Panel ── */
  const selectedCount = Object.values(toggles).filter(Boolean).length;

  return (
    <div className="space-y-5">
      <div className="flex flex-wrap items-center justify-between gap-3">
        <div>
          <h1 className="flex items-center gap-2 text-2xl font-bold tracking-tight">
            <Shield className="h-5 w-5 text-brand" /> Admin paneli
          </h1>
          <p className="mt-1 text-sm text-ink-muted">
            {adminName ?? "admin"} (admin) — scraping pipeline və məlumat idarəetməsi
          </p>
        </div>
        <button
          onClick={logout}
          className="rounded-lg border border-line px-3 py-2 text-sm font-medium text-ink-muted hover:bg-surface-2 hover:text-ink"
        >
          Çıxış
        </button>
      </div>

      {message && (
        <p
          className={
            message.kind === "ok"
              ? "rounded-lg border border-success/30 bg-success/10 p-3 text-sm text-success"
              : "rounded-lg border border-danger/30 bg-danger/10 p-3 text-sm text-danger"
          }
        >
          {message.text}
        </p>
      )}

      <div className="grid gap-4 lg:grid-cols-[1fr_320px]">
        <div className="space-y-4">
          <div className="card p-4">
            <div className="mb-3 flex items-center justify-between">
              <h2 className="text-sm font-bold text-ink">Pipeline addımları</h2>
              <span className="text-xs text-ink-faint">{selectedCount} addım seçilib</span>
            </div>

            <div className="space-y-4">
              {GROUPS.map((group) => (
                <div key={group.title}>
                  <p className="mb-1.5 text-[10px] font-semibold uppercase tracking-wide text-ink-faint">
                    {group.title}
                  </p>
                  <div className="grid gap-2 sm:grid-cols-2 lg:grid-cols-3">
                    {group.keys.map((key) => (
                      <Toggle
                        key={`${group.title}-${key}`}
                        label={`${group.title} · ${LABELS[key]}`}
                        checked={toggles[key]}
                        disabled={state?.is_running}
                        onChange={(checked) =>
                          setToggles((prev) => ({ ...prev, [key]: checked }))
                        }
                      />
                    ))}
                  </div>
                </div>
              ))}
            </div>

            <div className="mt-4 flex flex-wrap gap-2 border-t border-line pt-4">
              <button
                onClick={startPipeline}
                disabled={busy || state?.is_running || selectedCount === 0}
                className="inline-flex items-center gap-2 rounded-lg bg-brand px-4 py-2 text-sm font-semibold text-white transition-opacity hover:opacity-90 disabled:opacity-50"
              >
                {busy ? <Loader2 className="h-4 w-4 animate-spin" /> : <Play className="h-4 w-4" />}
                Pipeline-i başlat
              </button>
              <button
                onClick={() => runFootyStats("games")}
                disabled={busy}
                className="inline-flex items-center gap-2 rounded-lg border border-line px-3 py-2 text-sm font-medium text-ink hover:bg-surface-2 disabled:opacity-50"
              >
                <Database className="h-4 w-4" /> FootyStats oyunları
              </button>
              <button
                onClick={() => runFootyStats("stats")}
                disabled={busy}
                className="inline-flex items-center gap-2 rounded-lg border border-line px-3 py-2 text-sm font-medium text-ink hover:bg-surface-2 disabled:opacity-50"
              >
                <Database className="h-4 w-4" /> FootyStats statistika
              </button>
              <button
                onClick={clearDb}
                disabled={busy}
                className="inline-flex items-center gap-2 rounded-lg border border-danger/40 bg-danger/10 px-3 py-2 text-sm font-semibold text-danger transition-colors hover:bg-danger/20 disabled:opacity-50"
              >
                <Trash2 className="h-4 w-4" /> Bazanı təmizlə
              </button>
            </div>
          </div>
        </div>

        <div className="space-y-4">
          <PipelineStatusCard state={state} />
          {state && (
            <div className="card p-3.5">
              <ProgressBar value={state.progress} status={state.step_status} />
            </div>
          )}
          <PipelineReport report={state?.report ?? null} />
        </div>
      </div>
    </div>
  );
}
