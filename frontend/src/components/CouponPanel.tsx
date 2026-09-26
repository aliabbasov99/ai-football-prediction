"use client";

import { AnimatePresence, motion, useReducedMotion } from "framer-motion";
import {
  Download,
  Receipt,
  Ticket,
  Trash2,
  TriangleAlert,
  X,
} from "lucide-react";
import { useRef, useState } from "react";
import { CouponItemRow } from "@/components/CouponItemRow";
import {
  hasConflictingSelections,
  potentialReturn,
  totalOdds,
} from "@/components/couponUtils";
import { useCoupon } from "@/context/CouponContext";
import { EXPORT_BG, EXPORT_SCALE } from "@/constants";
import { DUR, EASE_OUT } from "@/components/motion";

export function CouponPanel() {
  const { items, stake, setStake, isOpen, close, remove, clear } = useCoupon();
  const panelRef = useRef<HTMLDivElement>(null);
  const [exporting, setExporting] = useState(false);
  const reduce = useReducedMotion();

  const conflict = hasConflictingSelections(items);
  const odds = totalOdds(items);
  const ret = potentialReturn(items, stake);

  async function exportPng() {
    if (!panelRef.current || exporting) return;
    setExporting(true);
    try {
      const html2canvas = (await import("html2canvas-oklch")).default;
      const canvas = await html2canvas(panelRef.current, {
        backgroundColor: EXPORT_BG,
        scale: EXPORT_SCALE,
      });
      const link = document.createElement("a");
      link.download = `kupon-${Date.now()}.png`;
      link.href = canvas.toDataURL("image/png");
      link.click();
    } catch {
      alert("PNG ixracı alına bilmədi.");
    } finally {
      setExporting(false);
    }
  }

  return (
    <>
      <AnimatePresence>
        {isOpen && (
          <motion.div
            initial={reduce ? false : { opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={reduce ? undefined : { opacity: 0 }}
            transition={{ duration: DUR.base, ease: EASE_OUT }}
            onClick={close}
            className="fixed inset-0 z-40 bg-black/70 backdrop-blur-sm"
            aria-hidden
          />
        )}
      </AnimatePresence>

      <motion.aside
        initial={false}
        animate={{ x: isOpen ? 0 : "100%" }}
        transition={{ duration: DUR.slow, ease: EASE_OUT }}
        className="coupon-export fixed right-0 top-0 z-50 flex h-full w-full max-w-sm flex-col border-l border-line bg-base"
        aria-hidden={!isOpen}
      >
        <div className="flex items-center justify-between border-b border-line bg-surface/60 px-4 py-3 backdrop-blur-sm">
          <h2 className="flex items-center gap-2 text-sm font-semibold">
            <Ticket className="h-4 w-4 text-brand" strokeWidth={2.25} />
            Kupon
            {items.length > 0 && (
              <span className="pill badge-muted">{items.length}</span>
            )}
          </h2>
          <button
            onClick={close}
            className="btn btn-ghost !px-2 !py-1.5"
            aria-label="Bağla"
          >
            <X className="h-4 w-4" strokeWidth={2.25} />
          </button>
        </div>

        <div ref={panelRef} className="flex min-h-0 flex-1 flex-col bg-surface/50">
          <div className="flex-1 space-y-2 overflow-y-auto p-4">
            {items.length === 0 ? (
              <div className="grid place-items-center gap-3 py-16 text-center">
                <span className="grid h-14 w-14 place-items-center rounded-xl border border-line bg-surface-2">
                  <Ticket className="h-6 w-6 text-ink-faint" strokeWidth={1.75} />
                </span>
                <p className="text-sm font-medium text-ink">Kupon boşdur</p>
                <p className="max-w-[240px] text-xs leading-relaxed text-ink-faint">
                  Proqnozlar səhifəsində əmsal seçdikdə məhsullar burada toplanacaq.
                </p>
              </div>
            ) : (
              items.map((item) => (
                <CouponItemRow key={item.key} item={item} onRemove={remove} />
              ))
            )}
          </div>

          {items.length > 0 && (
            <div className="space-y-4 border-t border-line bg-surface/80 p-4 backdrop-blur-sm">
              <AnimatePresence>
                {conflict && (
                  <motion.p
                    initial={reduce ? false : { opacity: 0, height: 0 }}
                    animate={{ opacity: 1, height: "auto" }}
                    exit={reduce ? undefined : { opacity: 0, height: 0 }}
                    transition={{ duration: DUR.base, ease: EASE_OUT }}
                    className="flex items-start gap-2 overflow-hidden rounded-lg border border-warn/30 bg-warn/10 p-2.5 text-xs leading-relaxed text-warn"
                  >
                    <TriangleAlert
                      className="mt-0.5 h-3.5 w-3.5 shrink-0"
                      strokeWidth={2.25}
                    />
                    <span>
                      Eyni matçda bir-birini əks edən seçimlər var (məs. 1 və 2). Bu kupon
                      uğurlu ola bilməz.
                    </span>
                  </motion.p>
                )}
              </AnimatePresence>

              <label className="block text-xs font-medium text-ink-muted">
                Stake (AZN)
                <input
                  type="number"
                  min={0}
                  step={1}
                  value={stake}
                  onChange={(e) => setStake(Math.max(0, Number(e.target.value) || 0))}
                  className="input mt-1.5 !font-semibold"
                />
              </label>

              <div className="card-inset space-y-1.5 p-3 text-sm">
                <div className="flex justify-between text-ink-muted">
                  <span>Ümumi əmsal</span>
                  <span className="font-semibold tabular-nums text-ink">
                    {odds.toFixed(2)}
                  </span>
                </div>
                <div className="flex justify-between text-ink-muted">
                  <span>Məqsud</span>
                  <span className="font-semibold tabular-nums text-success">
                    {ret.toFixed(2)} AZN
                  </span>
                </div>
              </div>

              <div className="flex gap-2">
                <button
                  onClick={exportPng}
                  disabled={exporting}
                  className="btn btn-ghost flex-1"
                >
                  <Download className="h-4 w-4" strokeWidth={2.25} />
                  {exporting ? "İxrac…" : "PNG"}
                </button>
                <button onClick={clear} className="btn btn-danger">
                  <Trash2 className="h-4 w-4" strokeWidth={2.25} />
                  Təmizlə
                </button>
              </div>

              <p className="flex items-center justify-center gap-1.5 text-[11px] text-ink-faint">
                <Receipt className="h-3 w-3" strokeWidth={2.25} />
                Bu proqnozlar məlumat üçündür, məsləhət deyil
              </p>
            </div>
          )}
        </div>
      </motion.aside>
    </>
  );
}
