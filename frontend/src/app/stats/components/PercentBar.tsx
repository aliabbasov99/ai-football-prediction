import { cn } from "@/lib/utils";

/** 0-100 aralığında faiz göstəricisi. */
export function PercentBar({ value, tone = "info" }: { value: number; tone?: "info" | "success" | "warn" | "danger" }) {
  const clamped = Math.max(0, Math.min(100, value));
  const bg =
    tone === "success"
      ? "bg-success"
      : tone === "warn"
        ? "bg-warn"
        : tone === "danger"
          ? "bg-danger"
          : "bg-info";

  return (
    <div className="h-1.5 w-full overflow-hidden rounded-full bg-surface-3">
      <div className={cn("h-full rounded-full transition-all", bg)} style={{ width: `${clamped}%` }} />
    </div>
  );
}
