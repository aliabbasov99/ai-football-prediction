"use client";

import {
  AlertTriangle,
  Check,
  Layers,
  Loader2,
  Plus,
  RefreshCw,
  Save,
  Trash2,
} from "lucide-react";
import { AnimatePresence, motion, useReducedMotion } from "framer-motion";
import { useCallback, useEffect, useState } from "react";
import { TeamLogo } from "@/app/predictions/components/TeamLogo";
import { EmptyState } from "@/components/EmptyState";
import { DUR, EASE_OUT, Reveal } from "@/components/motion";
import { api, ApiError } from "@/lib/api";
import { cn } from "@/lib/utils";
import { useAuth } from "@/lib/useAuth";
import type { AdminTeam, LeagueConfig } from "@/types/football";

const BLANK_LEAGUE: Partial<LeagueConfig> = {
  name: "",
  country: "",
  logo: "",
  wincomparator_link: "",
  betimate_link: "",
  sportsgambler_link: "",
  footystats_link: "",
};

export default function AdminLeaguesPage() {
  const [leagues, setLeagues] = useState<LeagueConfig[]>([]);
  const [teams, setTeams] = useState<AdminTeam[]>([]);
  const [selectedLeague, setSelectedLeague] = useState<string | null>(null);
  const [draft, setDraft] = useState<Partial<LeagueConfig>>(BLANK_LEAGUE);
  const [busy, setBusy] = useState(false);
  const [message, setMessage] = useState<{ kind: "ok" | "err"; text: string } | null>(null);

  const { status, isAdmin, refresh } = useAuth();
  const reduce = useReducedMotion();

  const loadLeagues = useCallback(async () => {
    try {
      const res = await api.adminLeagues();
      setLeagues(res ?? []);
    } catch (e) {
      setMessage({ kind: "err", text: e instanceof ApiError ? e.message : "Xəta" });
    }
  }, []);

  // `setTimeout` callback-i ilə çağırılır ki, effect gövdəsində birbaşa
  // setState olmasın (React 19 `set-state-in-effect` qaydası).
  useEffect(() => {
    if (!isAdmin) return;
    const t = setTimeout(() => void loadLeagues(), 0);
    return () => clearTimeout(t);
  }, [isAdmin, loadLeagues, refresh]);

  const loadTeams = useCallback(async (leagueId: string) => {
    try {
      const res = await api.adminTeams(leagueId);
      setTeams(res.teams ?? []);
    } catch (e) {
      setMessage({ kind: "err", text: e instanceof ApiError ? e.message : "Xəta" });
    }
  }, []);

  async function run<T>(fn: () => Promise<T>, okText: string) {
    setBusy(true);
    setMessage(null);
    try {
      await fn();
      setMessage({ kind: "ok", text: okText });
    } catch (e) {
      setMessage({ kind: "err", text: e instanceof ApiError ? e.message : "Xəta baş verdi" });
    } finally {
      setBusy(false);
    }
  }

  if (status === "loading") {
    return (
      <div className="grid place-items-center py-20">
        <Loader2 className="h-6 w-6 animate-spin text-ink-faint" />
      </div>
    );
  }

  if (!isAdmin) {
    return (
      <EmptyState
        icon={AlertTriangle}
        title="Admin girişi tələb olunur"
        description="Bu səhifəyə daxil olmaq üçün əvvəlcə /admin səhifəsindən giriş edin."
      />
    );
  }

  return (
    <div className="space-y-6">
      <Reveal>
        <div>
          <h1 className="flex items-center gap-2 text-2xl font-semibold tracking-tight">
            <Layers className="h-5.5 w-5.5 text-brand" strokeWidth={2.25} />
            Liqa və komanda idarəetməsi
          </h1>
          <p className="mt-1 text-sm text-ink-muted">
            Liqa konfiqurasiyaları, mənbə linkləri, komanda loqoları və alias-lar.
          </p>
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
            className={cn(
              "rounded-xl border p-3 text-sm",
              message.kind === "ok"
                ? "border-success/30 bg-success/10 text-success"
                : "border-danger/30 bg-danger/10 text-danger",
            )}
          >
            {message.text}
          </motion.p>
        )}
      </AnimatePresence>

      <div className="grid gap-6 lg:grid-cols-[320px_1fr]">
        {/* ── Liqalar ── */}
        <Reveal className="space-y-4">
          <div className="card overflow-hidden">
            <div className="flex items-center justify-between border-b border-line bg-surface-2 px-3 py-2.5">
              <h2 className="text-sm font-semibold text-ink">Liqalar ({leagues.length})</h2>
              <button
                onClick={() => {
                  setDraft(BLANK_LEAGUE);
                  setSelectedLeague(null);
                  setTeams([]);
                }}
                className="btn btn-ghost !px-2 !py-1 !text-xs"
              >
                <Plus className="h-3.5 w-3.5" /> Yeni
              </button>
            </div>

            {leagues.length === 0 ? (
              <p className="px-3 py-6 text-center text-sm text-ink-faint">Liqa yoxdur</p>
            ) : (
              <ul className="max-h-80 divide-y divide-line-soft overflow-y-auto">
                {leagues.map((league) => (
                  <li key={league._id}>
                    <button
                      onClick={() => {
                        setSelectedLeague(league._id ?? null);
                        setDraft(league);
                        if (league._id) void loadTeams(league._id);
                      }}
                      className={`flex w-full items-center justify-between gap-2 px-3 py-2 text-left text-sm transition-colors ${
                        selectedLeague === league._id
                          ? "bg-surface-3 text-ink"
                          : "text-ink-muted hover:bg-surface-2"
                      }`}
                    >
                      <span className="min-w-0 flex-1 truncate">{league.name}</span>
                      {selectedLeague === league._id && <Check className="h-3.5 w-3.5 text-brand" />}
                    </button>
                  </li>
                ))}
              </ul>
            )}
          </div>

          <button
            onClick={() => void loadLeagues()}
            className="btn btn-ghost w-full"
          >
            <RefreshCw className="h-4 w-4" strokeWidth={2.25} /> Yenilə
          </button>
        </Reveal>

        {/* ── Redaktə + komandalar ── */}
        <div className="space-y-6">
          <div className="card p-4">
            <h2 className="mb-3 text-sm font-semibold text-ink">
              {selectedLeague ? "Liqanı redaktə et" : "Yeni liqa əlavə et"}
            </h2>

            <div className="grid gap-3 sm:grid-cols-2">
              <label className="block text-xs font-medium text-ink-muted">
                Ad
                <input
                  value={draft.name ?? ""}
                  onChange={(e) => setDraft((d) => ({ ...d, name: e.target.value }))}
                  className="input mt-1"
                />
              </label>
              <label className="block text-xs font-medium text-ink-muted">
                Ölkə
                <input
                  value={draft.country ?? ""}
                  onChange={(e) => setDraft((d) => ({ ...d, country: e.target.value }))}
                  className="input mt-1"
                />
              </label>
              <label className="block text-xs font-medium text-ink-muted sm:col-span-2">
                Loqo (URL və ya lokal yol)
                <input
                  value={draft.logo ?? ""}
                  onChange={(e) => setDraft((d) => ({ ...d, logo: e.target.value }))}
                  placeholder="https://… və ya /imgs/logos/leagues/premier_league.png"
                  className="input mt-1"
                />
              </label>

              {(
                [
                  ["wincomparator_link", "WinComparator listing"],
                  ["betimate_link", "Betimate listing"],
                  ["sportsgambler_link", "SportsGambler listing"],
                  ["footystats_link", "FootyStats link"],
                ] as const
              ).map(([key, label]) => (
                <label key={key} className="block text-xs font-medium text-ink-muted">
                  {label}
                  <input
                    value={draft[key] ?? ""}
                    onChange={(e) => setDraft((d) => ({ ...d, [key]: e.target.value }))}
                    className="input mt-1"
                  />
                </label>
              ))}
            </div>

            <div className="mt-4 flex flex-wrap gap-2 border-t border-line pt-4">
              <button
                disabled={busy || !draft.name}
                onClick={() =>
                  void run(async () => {
                    if (selectedLeague) await api.adminUpdateLeague(selectedLeague, draft);
                    else await api.adminCreateLeague(draft);
                    await loadLeagues();
                  }, selectedLeague ? "Liqa yeniləndi" : "Liqa əlavə edildi")
                }
                className="btn btn-primary"
              >
                <Save className="h-4 w-4" /> Yadda saxla
              </button>

              {selectedLeague && (
                <>
                  <button
                    disabled={busy}
                    onClick={() =>
                      void run(async () => {
                        await api.adminSyncTeams(selectedLeague);
                        await loadTeams(selectedLeague);
                      }, "Komandalar sinxronizasiya edildi")
                    }
                    className="btn btn-ghost"
                  >
                    <RefreshCw className="h-4 w-4" /> Komandaları sinxronlaşdır
                  </button>
                  <button
                    disabled={busy}
                    onClick={() => {
                      if (!confirm(`"${draft.name}" silinsin?`)) return;
                      void run(async () => {
                        await api.adminDeleteLeague(selectedLeague);
                        setSelectedLeague(null);
                        setTeams([]);
                        setDraft(BLANK_LEAGUE);
                        await loadLeagues();
                      }, "Liqa silindi");
                    }}
                    className="btn btn-danger"
                  >
                    <Trash2 className="h-4 w-4" /> Sil
                  </button>
                </>
              )}
            </div>
          </div>

          {/* ── Komandalar ── */}
          {selectedLeague && (
            <div className="card overflow-hidden">
              <div className="flex items-center justify-between border-b border-line bg-surface-2 px-3 py-2.5">
                <h2 className="text-sm font-semibold text-ink">Komandalar ({teams.length})</h2>
              </div>

              {teams.length === 0 ? (
                <p className="px-3 py-8 text-center text-sm text-ink-faint">
                  Komanda yoxdur — &quot;Komandaları sinxronlaşdır&quot; düyməsini
                  istifadə edin.
                </p>
              ) : (
                <div className="max-h-96 overflow-y-auto">
                  <table className="w-full text-sm">
                    <thead className="sticky top-0 bg-surface-2">
                      <tr className="border-b border-line text-left">
                        <th className="px-3 py-2 font-semibold text-ink-muted">Ad</th>
                        <th className="px-3 py-2 font-semibold text-ink-muted">Loqo</th>
                        <th className="px-3 py-2 font-semibold text-ink-muted">Alias-lar</th>
                        <th className="w-10" />
                      </tr>
                    </thead>
                    <tbody>
                      {teams.map((team) => (
                        <TeamRow
                          key={team._id}
                          team={team}
                          disabled={busy}
                          onSave={(data) =>
                            run(async () => {
                              await api.adminUpdateTeam(team._id, data);
                              await loadTeams(selectedLeague);
                            }, `${team.name} yeniləndi`)
                          }
                          onDelete={() =>
                            run(async () => {
                              await api.adminDeleteTeam(team._id);
                              await loadTeams(selectedLeague);
                            }, `${team.name} silindi`)
                          }
                        />
                      ))}
                    </tbody>
                  </table>
                </div>
              )}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

/** Bir komanda sətri — loqo və alias sahələri redaktə oluna bilər. */
function TeamRow({
  team,
  disabled,
  onSave,
  onDelete,
}: {
  team: AdminTeam;
  disabled: boolean;
  onSave: (data: Partial<AdminTeam>) => void;
  onDelete: () => void;
}) {
  const [logo, setLogo] = useState(team.logo ?? "");
  const [aliases, setAliases] = useState((team.aliases ?? []).join(", "));
  const [dirty, setDirty] = useState(false);

  return (
    <tr className="border-b border-line-soft last:border-0">
      <td className="px-3 py-1.5 font-medium text-ink">{team.name}</td>
      <td className="px-3 py-1.5">
        <div className="flex items-center gap-2">
          {/* Canlı önizləmə: admin loqonun düzgün qurulduğunu dərhal görür */}
          <TeamLogo logo={logo} name={team.name} size={24} alt={team.name} />
          <input
            value={logo}
            onChange={(e) => {
              setLogo(e.target.value);
              setDirty(true);
            }}
            placeholder="URL və ya /imgs/logos/teams/arsenal.png"
            className="input min-w-[160px] !px-2 !py-1 !text-xs"
          />
        </div>
      </td>
      <td className="px-3 py-1.5">
        <input
          value={aliases}
          onChange={(e) => {
            setAliases(e.target.value);
            setDirty(true);
          }}
          placeholder="alias1, alias2"
          className="input min-w-[180px] !px-2 !py-1 !text-xs"
        />
      </td>
      <td className="px-2 py-1.5">
        <div className="flex gap-1">
          <button
            disabled={disabled || !dirty}
            onClick={() => {
              onSave({
                logo,
                aliases: aliases
                  .split(",")
                  .map((a) => a.trim())
                  .filter(Boolean),
              });
              setDirty(false);
            }}
            className="grid h-7 w-7 place-items-center rounded-md bg-success/15 text-success disabled:opacity-30"
            aria-label="Yadda saxla"
          >
            <Save className="h-3.5 w-3.5" />
          </button>
          <button
            disabled={disabled}
            onClick={onDelete}
            className="grid h-7 w-7 place-items-center rounded-md bg-danger/15 text-danger disabled:opacity-30"
            aria-label="Sil"
          >
            <Trash2 className="h-3.5 w-3.5" />
          </button>
        </div>
      </td>
    </tr>
  );
}
