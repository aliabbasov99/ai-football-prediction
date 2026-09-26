import { Lock } from "lucide-react";

/** Məlumatı olmayan bazalar üçün kilit işarəsi. */
export function LockIcon({ title = "Məlumat yoxdur" }: { title?: string }) {
  return (
    <span
      title={title}
      aria-label={title}
      className="inline-grid h-6 w-6 place-items-center rounded-md bg-surface-2 text-ink-faint"
    >
      <Lock className="h-3 w-3" />
    </span>
  );
}
