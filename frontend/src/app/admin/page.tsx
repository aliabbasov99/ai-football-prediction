"use client";

import { AnimatePresence, motion, useReducedMotion } from "framer-motion";
import {
  AlertTriangle,
  CircuitBoard,
  Database,
  Gauge,
  Layers,
  Loader2,
  LogIn,
  Rocket,
  ShieldCheck,
  Trash2,
  TriangleAlert,
} from "lucide-react";
import { useCallback, useEffect, useState } from "react";
import {
  PipelineLog,
  PipelineReport,
  PipelineStatusCard,
} from "./components/PipelineReport";
import { ProgressBar } from "./components/ProgressBar";
import { Toggle } from "./components/Toggle";
import { api, ApiError, getToken, setToken } from "@/lib/api";
import { useAuth } from "@/lib/useAuth";
import { DUR, EASE_OUT, Reveal } from "@/components/motion";
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
  const [leagueCount, setLeagueCount] = useState<number | null>(null);

  const { status, isAdmin, nickname: adminName, refresh, logout: logoutAuth } =
    useAuth();
  const reduce = useReducedMotion();

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

  /**
   * ÖNCƏKİ YOXLAMA — pipeline düyməsinin "heç nə olmur" probleminin əsas səbəbi:
   * DB-də lig yoxdursa skriptlər heç nə tapa bilmir və pipeline boş report
   * ilə bitir. İstifadəçi isə "düymə işləmir" deyirdi.
   */
  useEffect(() => {
    if (!isAdmin) return;
    let cancelled = false;
    (async () => {
      try {
        const leagues = await api.adminLeagues();
        if (!cancelled) setLeagueCount(leagues.length);
      } catch {
        if (!cancelled) setLeagueCount(null);
      }
    })();
    return () => {
      cancelled = true;
    };
  }, [isAdmin]);

  async function login(e: React.FormEvent) {
    e.preventDefault();
    setAuthLoading(true);
    setAuthError(null);
    try {
      const res = await api.login(nickname, password);
      setToken(res.access_token);
      setPassword("");
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
    // Boş DB ilə pipeline işə salınma — səbəbini əvvəlcədən de
    if (leagueCount === 0) {
      setMessage({
        kind: "err",
        text:
          "Heç bir lig təyin edilməyib. Pipeline məlumat çəkmək üçün əvvəlcə " +
          "`/admin/leagues` bölməsindən ən azı bir lig əlavə edin.",
      });
      return;
    }

    setBusy(true);
    setMessage(null);
    try {
      const res = await api.adminScrapeStart(toggles);
      setMessage({
        kind: res.status === "warning" ? "err" : "ok",
        text:
          res.message ??
          (res.status === "warning" ? "Pipeline artıq işləyir" : "Pipeline başladı"),
      });
      // Dərhal bir dəfə çək — düymə "başladı" vəziyyətini dərhal göstərsin
      void poll();
    } catch (e) {
      setMessage({
        kind: "err",
        text: e instanceof ApiError ? e.message : "Xəta baş verdi",
      });
    } finally {
      setBusy(false);
    }
  }

  async function clearDb() {
    if (
      !confirm("Bütün məlumat bazaları silinsin? Bu əməliyat geri qaytarıla bilməz.")
    )
      return;
    setBusy(true);
    setMessage(null);
    try {
      const res = await api.adminClearDb();
      setMessage({ kind: "ok", text: res.message ?? "Baza təmizləndi" });
      void poll();
    } catch (e) {
      setMessage({
        kind: "err",
        text: e instanceof ApiError ? e.message : "Xəta baş verdi",
      });
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
      setMessage({
        kind: "err",
        text: e instanceof ApiError ? e.message : "Xəta baş verdi",
      });
    } finally {
      setBusy(false);
    }
  }

  /* ── Giriş ekranı ── */
  if (status === "loading") {
    return (
      <div className="grid place-items-center py-20">
        <Loader2 className="h-6 w-6 animate-spin text-ink-faint" strokeWidth={2.25} />
      </div>
    );
  }

  if (!isAdmin) {
    return (
      <div className="mx-auto max-w-sm py-10">
        <Reveal>
          <div className="card p-6">
            <h1 className="flex items-center gap-2 text-lg font-semibold">
              <ShieldCheck className="h-5 w-5 text-brand" strokeWidth={2.25} />
              Admin girişi
            </h1>
            <p className="mt-1.5 text-sm text-ink-muted">
              Bu səhifə yalnız administrator üçün. Admin hesabı ilə daxil olun.
            </p>

            <form onSubmit={login} className="mt-6 space-y-3">
              <input
                value={nickname}
                onChange={(e) => setNickname(e.target.value)}
                placeholder="İstifadəçi adı"
                autoComplete="username"
                className="input"
              />
              <input
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                placeholder="Şifrə"
                autoComplete="current-password"
                className="input"
              />

              <AnimatePresence>
                {authError && (
                  <motion.p
                    initial={reduce ? false : { opacity: 0, y: -4 }}
                    animate={{ opacity: 1, y: 0 }}
                    exit={reduce ? undefined : { opacity: 0 }}
                    transition={{ duration: DUR.fast, ease: EASE_OUT }}
                    className="flex items-center gap-1.5 text-xs text-danger"
                  >
                    <TriangleAlert className="h-3.5 w-3.5" strokeWidth={2.5} />
                    {authError}
                  </motion.p>
                )}
              </AnimatePresence>

              <button
                type="submit"
                disabled={authLoading}
                className="btn btn-primary w-full"
              >
                {authLoading ? (
                  <Loader2 className="h-4 w-4 animate-spin" strokeWidth={2.5} />
                ) : (
                  <LogIn className="h-4 w-4" strokeWidth={2.25} />
                )}
                Daxil ol
              </button>
            </form>
          </div>
        </Reveal>
      </div>
    );
  }

  /* ── Panel ── */
  const selectedCount = Object.values(toggles).filter(Boolean).length;
  const noLeagues = leagueCount === 0;

  return (
    <div className="space-y-6">
      <Reveal>
        <div className="flex flex-wrap items-start justify-between gap-3">
          <div>
            <h1 className="flex items-center gap-2 text-2xl font-semibold tracking-tight">
              <ShieldCheck className="h-5.5 w-5.5 text-brand" strokeWidth={2.25} />
              Admin paneli
            </h1>
            <p className="mt-1 text-sm text-ink-muted">
              {adminName ?? "admin"} (admin) — scraping pipeline və məlumat idarəetməsi
            </p>
          </div>
          <button onClick={logout} className="btn btn-ghost">
            Çıxış
          </button>
        </div>
      </Reveal>

      <AnimatePresence>
        {message && (
          <motion.p
            key={message.text}
            initial={reduce ? false : { opacity: 0, y: -6 }}
            animate={{ opacity: 1, y: 0 }}
            exit={reduce ? undefined : { opacity: 0, y: -6 }}
            transition={{ duration: DUR.base, ease: EASE_OUT }}
            className={
              message.kind === "ok"
                ? "rounded-xl border border-success/30 bg-success/10 p-3 text-sm text-success"
                : "rounded-xl border border-danger/30 bg-danger/10 p-3 text-sm text-danger"
            }
          >
            {message.text}
          </motion.p>
        )}
      </AnimatePresence>

      {/* ── ÖNCƏKİ XƏBƏRDARLIQ: heç bir lig yoxdur ── */}
      <AnimatePresence>
        {noLeagues && (
          <motion.div
            initial={reduce ? false : { opacity: 0, y: -6 }}
            animate={{ opacity: 1, y: 0 }}
            exit={reduce ? undefined : { opacity: 0, y: -6 }}
            transition={{ duration: DUR.base, ease: EASE_OUT }}
            className="rounded-xl border border-warn/30 bg-warn/10 p-4"
          >
            <p className="flex items-center gap-2 text-sm font-medium text-warn">
              <AlertTriangle className="h-4 w-4" strokeWidth={2.25} />
              Heç bir lig təyin edilməyib
            </p>
            <p className="mt-1.5 text-sm leading-relaxed text-ink-muted">
              Pipeline yalnız DB-də təyin edilmiş liglər üçün oyun axtarır. Lig
              yoxdursa bütün skriptlər boş qaytarır və pipeline heç nə toplamadan
              bitir — bu, əvvəlki versiyalarda &laquo;düymə heç nə etmir&laquo; təsurrücünün
              səbəbi idi.
            </p>
            <a href="/admin/leagues" className="btn btn-ghost mt-3">
              <Layers className="h-4 w-4" strokeWidth={2.25} />
              Ligləri idarə et
            </a>
          </motion.div>
        )}
      </AnimatePresence>

      <div className="grid gap-6 lg:grid-cols-[1fr_340px]">
        <div className="space-y-6">
          <Reveal delay={0.05}>
            <div className="card p-6">
              <div className="mb-4 flex items-center justify-between gap-3">
                <h2 className="flex items-center gap-2 text-sm font-semibold text-ink">
                  <CircuitBoard className="h-4 w-4 text-ink-faint" strokeWidth={2.25} />
                  Pipeline addımları
                </h2>
                <span className="pill badge-muted">{selectedCount} addım seçilib</span>
              </div>

              <div className="space-y-6">
                {GROUPS.map((group) => (
                  <div key={group.title}>
                    <p className="mb-2 text-[10px] font-semibold uppercase tracking-wider text-ink-faint">
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

              <div className="mt-6 flex flex-wrap gap-2 border-t border-line pt-6">
                <motion.button
                  onClick={startPipeline}
                  disabled={busy || state?.is_running || selectedCount === 0}
                  whileHover={
                    reduce || busy || state?.is_running || selectedCount === 0
                      ? undefined
                      : { scale: 1.01 }
                  }
                  whileTap={
                    reduce || busy || state?.is_running || selectedCount === 0
                      ? undefined
                      : { scale: 0.98 }
                  }
                  transition={{ duration: DUR.fast, ease: EASE_OUT }}
                  className="btn btn-primary"
                >
                  {busy ? (
                    <Loader2 className="h-4 w-4 animate-spin" strokeWidth={2.5} />
                  ) : (
                    <Rocket className="h-4 w-4" strokeWidth={2.25} />
                  )}
                  Pipeline-i başlat
                </motion.button>
                <button
                  onClick={() => runFootyStats("games")}
                  disabled={busy}
                  className="btn btn-ghost"
                >
                  <Database className="h-4 w-4" strokeWidth={2.25} />
                  FootyStats oyunları
                </button>
                <button
                  onClick={() => runFootyStats("stats")}
                  disabled={busy}
                  className="btn btn-ghost"
                >
                  <Gauge className="h-4 w-4" strokeWidth={2.25} />
                  FootyStats statistika
                </button>
                <button onClick={clearDb} disabled={busy} className="btn btn-danger">
                  <Trash2 className="h-4 w-4" strokeWidth={2.25} />
                  Bazanı təmizlə
                </button>
              </div>

              {/* Düymənin yanında canlı vəziyyət — əvvəl yalnız yuxarıda idi */}
              {state?.is_running && (
                <p className="mt-3 flex items-center gap-2 text-xs text-ink-muted">
                  <motion.span
                    animate={reduce ? undefined : { opacity: [1, 0.35, 1] }}
                    transition={{ duration: 1.4, repeat: Infinity, ease: "easeInOut" }}
                    className="h-1.5 w-1.5 rounded-full bg-brand"
                  />
                  {state.current_step || "Pipeline işləyir…"} —{" "}
                  {state.progress}%
                </p>
              )}
            </div>
          </Reveal>

          {/* ── LOG: əvvəl yalnız backend konsolunda idi ── */}
          <Reveal delay={0.1}>
            <PipelineLog lines={state?.log ?? []} />
          </Reveal>
        </div>

        <div className="space-y-6">
          <Reveal delay={0.1}>
            <PipelineStatusCard state={state} />
          </Reveal>
          {state && (
            <Reveal delay={0.15}>
              <div className="card p-4">
                <ProgressBar value={state.progress} status={state.step_status} />
              </div>
            </Reveal>
          )}
          <Reveal delay={0.2}>
            <PipelineReport report={state?.report ?? null} />
          </Reveal>
        </div>
      </div>
    </div>
  );
}
