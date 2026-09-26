import { cn } from "@/lib/utils";

interface InlineChipProps {
  label: string;
  value?: string | null;
  selected?: boolean;
  onClick?: () => void;
  highlight?: "up" | "down" | "none";
  title?: string;
}

/** 1X2 / Over / BTTS sətirlərindəki kiçik seçim düyməsi. */
export function InlineChip({
  label,
  value,
  selected = false,
  onClick,
  highlight = "none",
  title,
}: InlineChipProps) {
  const tone =
    highlight === "up"
      ? "text-success"
      : highlight === "down"
        ? "text-danger"
        : "text-ink";

  const content = (
    <>
      <span className="text-ink-faint">{label}</span>
      <span className={cn("ml-1 font-bold tabular-nums", tone)}>{value ?? "—"}</span>
    </>
  );

  if (!onClick) {
    return (
      <span
        title={title}
        className="inline-flex items-center rounded-md bg-surface-2 px-1.5 py-0.5 text-[11px]"
      >
        {content}
      </span>
    );
  }

  return (
    <button
      onClick={onClick}
      title={title}
      disabled={!value}
      className={cn(
        "inline-flex items-center rounded-md px-1.5 py-0.5 text-[11px] transition-colors",
        selected
          ? "bg-brand text-white"
          : "bg-surface-2 hover:bg-surface-3 disabled:cursor-not-allowed disabled:opacity-45",
      )}
    >
      {selected ? <span className="font-bold">{label}</span> : content}
    </button>
  );
}
