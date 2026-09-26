"use client";

import { AlertTriangle, Download, Ticket, Trash2, X } from "lucide-react";
import { useRef, useState } from "react";
import { CouponItemRow } from "@/components/CouponItemRow";
import {
  hasConflictingSelections,
  potentialReturn,
  totalOdds,
} from "@/components/couponUtils";
import { useCoupon } from "@/context/CouponContext";
import { cn } from "@/lib/utils";

export function CouponPanel() {
  const { items, stake, setStake, isOpen, close, remove, clear } = useCoupon();
  const panelRef = useRef<HTMLDivElement>(null);
  const [exporting, setExporting] = useState(false);

  const conflict = hasConflictingSelections(items);
  const odds = totalOdds(items);
  const ret = potentialReturn(items, stake);

  async function exportPng() {
    if (!panelRef.current || exporting) return;
    setExporting(true);
    try {
      const html2canvas = (await import("html2canvas-oklch")).default;
      const canvas = await html2canvas(panelRef.current, {
        backgroundColor: "#0d1220",
        scale: 2,
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
      {isOpen && (
        <div
          className="fixed inset-0 z-40 bg-black/60 backdrop-blur-sm"
          onClick={close}
          aria-hidden
        />
      )}

      <aside
        className={cn(
          "coupon-export fixed right-0 top-0 z-50 flex h-full w-full max-w-sm flex-col border-l border-line bg-surface transition-transform duration-200",
          isOpen ? "translate-x-0" : "translate-x-full",
        )}
        aria-hidden={!isOpen}
      >
        <div className="flex items-center justify-between border-b border-line px-4 py-3">
          <h2 className="flex items-center gap-2 font-bold">
            <Ticket className="h-4 w-4 text-brand" /> Kupon
            {items.length > 0 && (
              <span className="rounded-full bg-surface-3 px-2 py-0.5 text-xs font-bold text-ink-muted">
                {items.length}
              </span>
            )}
          </h2>
          <button
            onClick={close}
            className="grid h-8 w-8 place-items-center rounded-lg text-ink-muted hover:bg-surface-2 hover:text-ink"
            aria-label="Bağla"
          >
            <X className="h-5 w-5" />
          </button>
        </div>

        <div ref={panelRef} className="flex min-h-0 flex-1 flex-col">
          <div className="flex-1 space-y-2 overflow-y-auto p-4">
            {items.length === 0 ? (
              <div className="grid place-items-center gap-2 py-16 text-center">
                <Ticket className="h-8 w-8 text-ink-faint" />
                <p className="text-sm text-ink-muted">Kupon boşdur</p>
                <p className="max-w-[220px] text-xs text-ink-faint">
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
            <div className="space-y-3 border-t border-line bg-surface-2 p-4">
              {conflict && (
                <div className="flex items-start gap-2 rounded-lg border border-warn/30 bg-warn/10 p-2.5 text-xs text-warn">
                  <AlertTriangle className="mt-0.5 h-3.5 w-3.5 shrink-0" />
                  <span>
                    Eyni matçda bir-birini əks edən seçimlər var (məs. 1 və 2). Bu kupon
                    uğurlu ola bilməz.
                  </span>
                </div>
              )}

              <label className="block text-xs font-medium text-ink-muted">
                Stake (AZN)
                <input
                  type="number"
                  min={0}
                  step={1}
                  value={stake}
                  onChange={(e) => setStake(Math.max(0, Number(e.target.value) || 0))}
                  className="mt-1.5 w-full rounded-lg border border-line bg-surface px-3 py-2 text-sm font-semibold text-ink outline-none focus:border-brand"
                />
              </label>

              <div className="space-y-1.5 rounded-lg border border-line bg-surface p-3 text-sm">
                <div className="flex justify-between text-ink-muted">
                  <span>Ümumi əmsal</span>
                  <span className="font-bold text-ink">{odds.toFixed(2)}</span>
                </div>
                <div className="flex justify-between text-ink-muted">
                  <span>Məqsud</span>
                  <span className="font-bold text-success">{ret.toFixed(2)} AZN</span>
                </div>
              </div>

              <div className="flex gap-2">
                <button
                  onClick={exportPng}
                  disabled={exporting}
                  className="inline-flex flex-1 items-center justify-center gap-2 rounded-lg border border-line bg-surface px-3 py-2 text-sm font-semibold text-ink transition-colors hover:bg-surface-3 disabled:opacity-50"
                >
                  <Download className="h-4 w-4" />
                  {exporting ? "İxrac…" : "PNG"}
                </button>
                <button
                  onClick={clear}
                  className="inline-flex items-center justify-center gap-2 rounded-lg border border-danger/40 bg-danger/10 px-3 py-2 text-sm font-semibold text-danger transition-colors hover:bg-danger/20"
                >
                  <Trash2 className="h-4 w-4" />
                  Təmizlə
                </button>
              </div>
            </div>
          )}
        </div>
      </aside>
    </>
  );
}
