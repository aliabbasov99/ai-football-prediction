/**
 * Minimal `cn()` — clsockə ehtiyac yoxdur, sadəcə şərti birləşdirmə.
 */
export function cn(...parts: Array<string | false | null | undefined>): string {
  return parts.filter(Boolean).join(" ");
}

/** "Manchester City" -> "manchester-city" */
export function slugify(value: string): string {
  return value
    .normalize("NFKD")
    .replace(/[\u0300-\u036f]/g, "")
    .toLowerCase()
    .replace(/[^a-z0-9]+/g, "-")
    .replace(/^-+|-+$/g, "");
}

/** "Manchester City" -> "MC" (1-2 hərf) */
export function initials(name: string): string {
  const words = name.trim().split(/\s+/).filter(Boolean);
  if (words.length === 0) return "?";
  if (words.length === 1) return words[0].slice(0, 2).toUpperCase();
  return (words[0][0] + words[words.length - 1][0]).toUpperCase();
}

/**
 * Komanda adından sabit rəng çıxarır — initials fallback üçün.
 * Eyni ad hər yerdə eyni rəngi alır (hash → hue).
 */
export function colorFromString(value: string): { bg: string; fg: string } {
  let hash = 0;
  for (let i = 0; i < value.length; i++) {
    hash = value.charCodeAt(i) + ((hash << 5) - hash);
  }
  const hue = Math.abs(hash) % 360;
  return {
    bg: `hsl(${hue} 55% 32%)`,
    fg: `hsl(${hue} 85% 82%)`,
  };
}

/** "2.15" -> 2.15, boş/yararsız dəyər -> null */
export function toNumber(value: string | number | null | undefined): number | null {
  if (value === null || value === undefined || value === "") return null;
  const n = typeof value === "number" ? value : parseFloat(String(value).replace(",", "."));
  return Number.isFinite(n) ? n : null;
}

/** "45%" -> 45 */
export function toPercent(value: string | number | null | undefined): number | null {
  const n = toNumber(value);
  return n === null ? null : n;
}

const DATE_FMT = new Intl.DateTimeFormat("az-AZ", {
  day: "2-digit",
  month: "2-digit",
  year: "numeric",
});

/** ISO/"12.05.2026" formatını "12.05.2026" edir. Format tanınmazsa orijinal sətir qaytarılır. */
export function formatDate(value: string | null | undefined): string {
  if (!value) return "";
  const parsed = new Date(value);
  if (Number.isNaN(parsed.getTime())) return value;
  return DATE_FMT.format(parsed);
}

/** Formalar üçün: "W", "D", "L" ardıcıllığı. */
export function splitForm(form: string): string[] {
  return (form ?? "").split(/[\s,]+/).filter(Boolean);
}
