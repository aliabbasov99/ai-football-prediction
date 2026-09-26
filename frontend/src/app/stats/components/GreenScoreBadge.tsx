import { cn } from "@/lib/utils";

/** Yaşıl "score" badge — statistika cədvəlindəki ən yüksək dəyəri vurur. */
export function GreenScoreBadge({
  value,
  isBest,
}: {
  value: string | number | null;
  isBest?: boolean;
}) {
  return (
    <span
      className={cn(
        "inline-block rounded-md px-1.5 py-0.5 text-xs font-bold tabular-nums",
        isBest ? "bg-success/15 text-success" : "text-ink-muted",
      )}
    >
      {value ?? "—"}
    </span>
  );
}
