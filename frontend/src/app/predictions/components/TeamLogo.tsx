"use client";

import { useState } from "react";import { logoCandidates, type LogoKind } from "@/lib/logo";
import { cn, colorFromString, initials } from "@/lib/utils";

interface TeamLogoProps {
  /** DB-dən gələn loqo URL/pathy və ya komanda adı */
  logo?: string | null;
  /** loqo boşdursa lokal fayl axtarılacaq ad */
  name?: string | null;
  kind?: LogoKind;
  size?: number;
  className?: string;
  /** komanda adı — initials fallback üçün */
  alt?: string;
}

/**
 * Loqo komponenti. Mənbə zənciri `logoCandidates()` tərəfindən verilir;
 * hamısı uğursuz olsa komanda adının monogramını göstərir (bozuk fayl yoxdur).
 */
export function TeamLogo({
  logo,
  name,
  kind = "teams",
  size = 28,
  className,
  alt,
}: TeamLogoProps) {
  const label = alt || name || "";
  const candidates = logoCandidates(logo || name, kind);

  // Yeni loqo gələndə zəncirin başından başla.
  // React-in "prop dəyişəndə state tənzimlə"Patternsı: render zamanında
  // müqayisə edib state-i düzəldirik (effect + setState yoxdur).
  const sourceKey = `${logo ?? ""}|${name ?? ""}|${kind}`;
  const [prevKey, setPrevKey] = useState(sourceKey);
  const [index, setIndex] = useState(0);

  if (prevKey !== sourceKey) {
    setPrevKey(sourceKey);
    setIndex(0);
  }

  const current = candidates[index];
  const exhausted = !current;

  if (exhausted) {
    const { bg, fg } = colorFromString(label || "AFC");
    return (
      <span
        aria-label={label}
        title={label}
        className={cn(
          "inline-flex shrink-0 items-center justify-center rounded-full font-bold select-none",
          className,
        )}
        style={{
          width: size,
          height: size,
          backgroundColor: bg,
          color: fg,
          fontSize: Math.max(9, size * 0.36),
        }}
      >
        {initials(label)}
      </span>
    );
  }

  return (
    <img
      src={current.src}
      alt={label}
      title={label}
      width={size}
      height={size}
      loading="lazy"
      onError={() => setIndex((i) => i + 1)}
      className={cn("shrink-0 object-contain", className)}
      style={{ width: size, height: size }}
    />
  );
}
