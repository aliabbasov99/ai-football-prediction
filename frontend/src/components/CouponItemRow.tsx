"use client";

import { Trash2 } from "lucide-react";
import { TeamLogo } from "@/app/predictions/components/TeamLogo";
import type { CouponSelection } from "@/components/couponUtils";

export function CouponItemRow({
  item,
  onRemove,
}: {
  item: CouponSelection;
  onRemove: (key: string) => void;
}) {
  return (
    <div className="flex items-start gap-2.5 rounded-lg border border-line-soft bg-surface-2 p-2.5">
      <div className="flex shrink-0 items-center -space-x-1.5">
        <TeamLogo logo={item.homeLogo} name={item.homeTeam} size={20} alt={item.homeTeam} />
        <TeamLogo logo={item.awayLogo} name={item.awayTeam} size={20} alt={item.awayTeam} />
      </div>

      <div className="min-w-0 flex-1">
        <p className="truncate text-xs font-semibold text-ink">
          {item.homeTeam} — {item.awayTeam}
        </p>
        <p className="mt-0.5 truncate text-[11px] text-ink-faint">
          {item.marketLabel} · <span className="text-info">{item.selection}</span>
        </p>
      </div>

      <div className="flex shrink-0 items-center gap-1.5">
        <span className="rounded-md bg-surface-3 px-1.5 py-0.5 text-xs font-bold text-ink">
          {item.odds}
        </span>
        <button
          onClick={() => onRemove(item.key)}
          className="grid h-6 w-6 place-items-center rounded-md text-ink-faint transition-colors hover:bg-danger/15 hover:text-danger"
          aria-label="Sil"
        >
          <Trash2 className="h-3.5 w-3.5" />
        </button>
      </div>
    </div>
  );
}
