import { cn } from "@/lib/utils";

/** "W D L W W" — W yaşıl, D sarı, L qırmızı. */
export function FormBadge({ form, className }: { form: string; className?: string }) {
  const items = (form ?? "").split(/[\s,]+/).filter(Boolean);
  if (items.length === 0) return null;

  return (
    <div className={cn("flex items-center gap-1", className)}>
      {items.map((result, i) => {
        const tone =
          result.toUpperCase() === "W"
            ? "bg-success/15 text-success"
            : result.toUpperCase() === "D"
              ? "bg-warn/15 text-warn"
              : "bg-danger/15 text-danger";
        return (
          <span
            key={i}
            className={cn("grid h-5 w-5 place-items-center rounded text-[10px] font-semibold", tone)}
          >
            {result}
          </span>
        );
      })}
    </div>
  );
}
