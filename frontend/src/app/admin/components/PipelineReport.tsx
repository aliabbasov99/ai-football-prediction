import { AnimatePresence, motion, useReducedMotion } from "framer-motion";
import {
  AlertCircle,
  AlertTriangle,
  CheckCircle2,
  ChevronDown,
  CircleDashed,
  Clock,
  Info,
  Layers,
  Terminal,
  TrendingDown,
  Zap,
} from "lucide-react";
import { useEffect, useRef, useState } from "react";
import type { PipelineReport as Report, PipelineState } from "@/types/football";
import { DUR, EASE_OUT } from "@/components/motion";
import { cn } from "@/lib/utils";

/* ── Status ──────────────────────────────────────────────────────────── */

const STATUS_META: Record<
  string,
  { label: string; cls: string; Icon: typeof CheckCircle2 }
> = {
  idle: { label: "Gözləyir", cls: "badge-muted", Icon: CircleDashed },
  running: { label: "İşləyir", cls: "badge-brand", Icon: Zap },
  completed: { label: "Tamamlandı", cls: "badge-ok", Icon: CheckCircle2 },
  partial: { label: "Konkret problemlə bitdi", cls: "badge-warn", Icon: AlertTriangle },
  error: { label: "Xəta", cls: "badge-err", Icon: AlertCircle },
};

/* ── Mənbə adları — UI-da insan oxuyan etiketlər ─────────────────────── */

const SCRAPER_LABELS: Record<string, { name: string; Icon: typeof Layers }> = {
  oddslot: { name: "Oddslot", Icon: TrendingDown },
  wincomparator: { name: "WinComparator", Icon: Layers },
  footystats: { name: "FootyStats", Icon: Layers },
  betimate: { name: "Betimate", Icon: Layers },
  sportsgambler: { name: "SportsGambler", Icon: Layers },
  misli: { name: "Misli.az", Icon: Layers },
};

/* ==========================================================================
   Pipeline vəziyyət kartı
   ========================================================================== */

export function PipelineStatusCard({ state }: { state: PipelineState | null }) {
  const reduce = useReducedMotion();
  if (!state) return null;

  const meta = STATUS_META[state.step_status] ?? STATUS_META.idle;
  const StatusIcon = meta.Icon;

  return (
    <div className="card p-4">
      <div className="flex items-center justify-between gap-3">
        <span className="text-sm font-semibold text-ink">Vəziyyət</span>
        <motion.span
          key={state.step_status}
          initial={reduce ? false : { opacity: 0, scale: 0.94 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ duration: DUR.fast, ease: EASE_OUT }}
          className={cn("pill", meta.cls)}
        >
          <StatusIcon className="h-3 w-3" strokeWidth={2.5} />
          {meta.label}
        </motion.span>
      </div>

      <dl className="mt-4 grid grid-cols-2 gap-4 text-xs">
        <div className="min-w-0">
          <dt className="text-ink-faint">Cari addım</dt>
          <dd className="mt-0.5 truncate font-medium text-ink" title={state.current_step}>
            {state.current_step || "—"}
          </dd>
        </div>
        <div>
          <dt className="text-ink-faint">İrəliləyiş</dt>
          <dd className="mt-0.5 font-medium tabular-nums text-ink">
            {state.progress}%
            {state.total_steps > 0 && (
              <span className="ml-1 text-ink-faint">
                ({state.current_step_index + 1}/{state.total_steps})
              </span>
            )}
          </dd>
        </div>
      </dl>

      {/* Başlama/ bitmə vaxtları — "heç nə olmur" hissinin əksinə */}
      {(state.started_at || state.finished_at) && (
        <p className="mt-3 flex items-center gap-1.5 border-t border-line-soft pt-3 text-[11px] text-ink-faint">
          <Clock className="h-3 w-3" strokeWidth={2.25} />
          {state.started_at && <span>Başladı: {formatTime(state.started_at)}</span>}
          {state.finished_at && (
            <>
              <span aria-hidden>·</span>
              <span>Bitdi: {formatTime(state.finished_at)}</span>
            </>
          )}
        </p>
      )}

      {state.error && (
        <p className="mt-3 rounded-lg border border-danger/30 bg-danger/10 p-2.5 text-xs text-danger">
          {state.error}
        </p>
      )}
    </div>
  );
}

function formatTime(iso: string) {
  const d = new Date(iso);
  return Number.isNaN(d.getTime())
    ? iso
    : d.toLocaleTimeString("az-AZ", { hour: "2-digit", minute: "2-digit", second: "2-digit" });
}

/* ==========================================================================
   Yekun hesabat
   ========================================================================== */

export function PipelineReport({ report }: { report: Report | null }) {
  const reduce = useReducedMotion();
  if (!report) return null;

  const sources = Object.entries(report.per_scraper ?? {});
  const failed = report.failed_steps ?? [];
  const notes = report.notes ?? [];
  const hasWork = sources.some(([, s]) => (s.with_link ?? 0) + (s.with_prediction ?? 0) > 0);

  return (
    <div className="card overflow-hidden">
      <div className="flex items-center justify-between gap-3 border-b border-line px-4 py-3">
        <h3 className="flex items-center gap-2 text-sm font-semibold text-ink">
          <Layers className="h-4 w-4 text-ink-faint" strokeWidth={2.25} />
          Yekun hesabat
        </h3>
        <span className={cn("pill", hasWork ? "badge-ok" : "badge-warn")}>
          {report.total_fixtures} oyun
        </span>
      </div>

      {/* Nəticə boşdursa — niyəsini İLK DƏFƏ göstər, "heç nə olmur" yoxdur */}
      <AnimatePresence initial={false}>
        {report.aborted && (
          <motion.div
            initial={reduce ? false : { height: 0, opacity: 0 }}
            animate={{ height: "auto", opacity: 1 }}
            exit={reduce ? undefined : { height: 0, opacity: 0 }}
            transition={{ duration: DUR.base, ease: EASE_OUT }}
            className="overflow-hidden"
          >
            <div className="flex gap-2.5 border-b border-line-soft bg-warn/10 px-4 py-3">
              <AlertTriangle
                className="mt-0.5 h-4 w-4 shrink-0 text-warn"
                strokeWidth={2.25}
              />
              <p className="text-xs leading-relaxed text-warn">{report.aborted}</p>
            </div>
          </motion.div>
        )}
      </AnimatePresence>

      {sources.length > 0 && (
        <ul className="divide-y divide-line-soft">
          {sources.map(([key, stats]) => {
            const meta = SCRAPER_LABELS[key] ?? { name: key, Icon: Layers };
            const SrcIcon = meta.Icon;
            const link = stats.with_link;
            const pred = stats.with_prediction;
            const thisRun = stats.this_run ?? {};
            const gained = (thisRun.link ?? 0) + (thisRun.prediction ?? 0);
            const any = (link ?? 0) + (pred ?? 0);

            return (
              <li
                key={key}
                className="flex items-center justify-between gap-3 px-4 py-2.5 text-sm"
              >
                <span className="flex min-w-0 items-center gap-2 text-ink-muted">
                  {any > 0 ? (
                    <CheckCircle2 className="h-3.5 w-3.5 shrink-0 text-success" strokeWidth={2.5} />
                  ) : (
                    <CircleDashed className="h-3.5 w-3.5 shrink-0 text-ink-faint" strokeWidth={2.25} />
                  )}
                  <SrcIcon className="h-3.5 w-3.5 shrink-0 text-ink-faint" strokeWidth={2.25} />
                  <span className="truncate">{meta.name}</span>
                </span>

                <span className="flex shrink-0 items-center gap-2 text-xs tabular-nums">
                  {link !== undefined && (
                    <span className={cn(link > 0 ? "text-ink" : "text-ink-faint")}>
                      {link} link
                    </span>
                  )}
                  {pred !== undefined && (
                    <span className={cn(pred > 0 ? "text-ink" : "text-ink-faint")}>
                      {pred} proqnoz
                    </span>
                  )}
                  {gained > 0 && <span className="pill badge-ok">+{gained}</span>}
                </span>
              </li>
            );
          })}
        </ul>
      )}

      {/* Uğursuz addımlar */}
      {failed.length > 0 && (
        <div className="border-t border-line-soft bg-danger/5 px-4 py-3">
          <p className="flex items-center gap-1.5 text-xs font-medium text-danger">
            <AlertCircle className="h-3.5 w-3.5" strokeWidth={2.5} />
            {failed.length} addım uğursuz oldu
          </p>
          <ul className="mt-1.5 space-y-0.5 pl-5 text-xs text-ink-muted">
            {failed.map((s) => (
              <li key={s} className="list-disc">
                {s}
              </li>
            ))}
          </ul>
        </div>
      )}

      {/* İzahatlar — səbəb buradadır */}
      {notes.length > 0 && (
        <div className="space-y-2 border-t border-line-soft px-4 py-3">
          {notes.map((n, i) => (
            <p
              key={i}
              className="flex gap-2 text-xs leading-relaxed text-ink-muted"
            >
              <Info className="mt-0.5 h-3.5 w-3.5 shrink-0 text-ink-faint" strokeWidth={2.25} />
              {n}
            </p>
          ))}
        </div>
      )}
    </div>
  );
}

/* ==========================================================================
   Pipeline logu — əvvəl stdout yalnız backend konsoluna düşürdü və istifadəçi
   "heç nə olmur" deyirdi. İndi canlı olaraq burada görünür.
   ========================================================================== */

export function PipelineLog({ lines }: { lines: string[] }) {
  const [open, setOpen] = useState(true);
  const boxRef = useRef<HTMLDivElement>(null);
  const reduce = useReducedMotion();
  const pinned = useRef(true);

  // Yeni sətir gələndə avtomatik sona scroll et (istifadəçi yuxarı qalxmayanda)
  useEffect(() => {
    if (pinned.current && boxRef.current) {
      boxRef.current.scrollTop = boxRef.current.scrollHeight;
    }
  }, [lines.length]);

  if (lines.length === 0) return null;

  const errors = lines.filter((l) => l.includes("[X]") || l.includes("[!]")).length;

  return (
    <div className="card overflow-hidden">
      <button
        onClick={() => setOpen((v) => !v)}
        className="flex w-full items-center justify-between gap-3 px-4 py-3 text-left transition-colors duration-150 hover:bg-surface-2"
        aria-expanded={open}
      >
        <span className="flex items-center gap-2 text-sm font-semibold text-ink">
          <Terminal className="h-4 w-4 text-ink-faint" strokeWidth={2.25} />
          Pipeline logu
          <span className="pill badge-muted">{lines.length}</span>
          {errors > 0 && <span className="pill badge-err">{errors} xəta</span>}
        </span>
        <motion.span
          animate={{ rotate: open ? 0 : -90 }}
          transition={{ duration: DUR.fast, ease: EASE_OUT }}
          className="text-ink-faint"
        >
          <ChevronDown className="h-4 w-4" strokeWidth={2.25} />
        </motion.span>
      </button>

      <AnimatePresence initial={false}>
        {open && (
          <motion.div
            initial={reduce ? false : { height: 0, opacity: 0 }}
            animate={{ height: "auto", opacity: 1 }}
            exit={reduce ? undefined : { height: 0, opacity: 0 }}
            transition={{ duration: DUR.base, ease: EASE_OUT }}
            className="overflow-hidden"
          >
            <div
              ref={boxRef}
              onScroll={(e) => {
                const el = e.currentTarget;
                // istifadəçi yuxarı qalxanda avtomatik scroll dayanır
                pinned.current =
                  el.scrollHeight - el.scrollTop - el.clientHeight < 24;
              }}
              className="log-view card-inset max-h-80 overflow-y-auto px-3 py-2.5"
            >
              {lines.map((line, i) => (
                <LogLine key={i} line={line} />
              ))}
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}

function LogLine({ line }: { line: string }) {
  const isError = line.includes("[X]") || line.includes("[!]");
  const isStep = line.startsWith("$") || /^\[\d+%\]/.test(line);
  return (
    <div
      className={cn(
        "whitespace-pre-wrap break-words",
        isError && "text-danger",
        !isError && isStep && "text-brand-soft",
        !isError && !isStep && "text-ink-muted",
      )}
    >
      {line}
    </div>
  );
}
