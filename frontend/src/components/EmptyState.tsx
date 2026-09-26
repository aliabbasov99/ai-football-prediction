import type { LucideIcon } from "lucide-react";
import { Inbox } from "lucide-react";

interface EmptyStateProps {
  icon?: LucideIcon;
  title: string;
  description?: string;
  action?: React.ReactNode;
}

/** DB boş olduqda bütün səhifələrdə göstərilir. */
export function EmptyState({ icon: Icon = Inbox, title, description, action }: EmptyStateProps) {
  return (
    <div className="card grid place-items-center gap-3 px-6 py-16 text-center">
      <span className="grid h-12 w-12 place-items-center rounded-full bg-surface-2">
        <Icon className="h-5 w-5 text-ink-faint" />
      </span>
      <div className="space-y-1">
        <p className="font-semibold text-ink">{title}</p>
        {description && (
          <p className="mx-auto max-w-md text-sm text-ink-faint">{description}</p>
        )}
      </div>
      {action}
    </div>
  );
}
