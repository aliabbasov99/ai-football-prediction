import type { LucideIcon } from "lucide-react";
import { Inbox } from "lucide-react";
import { motion, useReducedMotion } from "framer-motion";

interface EmptyStateProps {
  icon?: LucideIcon;
  title: string;
  description?: string;
  action?: React.ReactNode;
}

/** DB boş olduqda bütün səhifələrdə göstərilir. */
export function EmptyState({
  icon: Icon = Inbox,
  title,
  description,
  action,
}: EmptyStateProps) {
  const reduce = useReducedMotion();

  return (
    <motion.div
      initial={reduce ? false : { opacity: 0, y: 8 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.3, ease: [0.22, 1, 0.36, 1] }}
      className="card grid place-items-center gap-3 px-6 py-16 text-center"
    >
      <span className="grid h-12 w-12 place-items-center rounded-xl border border-line bg-surface-2">
        <Icon className="h-5 w-5 text-ink-faint" strokeWidth={2} />
      </span>
      <div className="space-y-1.5">
        <p className="font-semibold text-ink">{title}</p>
        {description && (
          <p className="mx-auto max-w-md text-sm leading-relaxed text-ink-muted">
            {description}
          </p>
        )}
      </div>
      {action}
    </motion.div>
  );
}
