/**
 * Loqo həlli. Prioritet zənciri:
 *   1) DB-dən gələn URL (skraperlar yazır — ən etibarlı mənbə)
 *   2) Uzaq URL (http/https)
 *   3) Lokal fayl: public/imgs/logos/{teams|leagues}/{slug}.{png|svg|webp|jpg}
 *   4) Heç biri işləməsə — komanda adının baş hərfləri (rəngli avatar)
 *
 * 4-cü addım "default şəkil" deyil: bozuk/placeholder fayl göstərmir,
 * komandanın öz adından generasiya olunan monogramdır.
 * Loqolar `scripts/fetch_logos.py` ilə əvvəlcədən endirilir.
 */
import { slugify } from "@/lib/utils";

export type LogoKind = "teams" | "leagues";

/** Skriptin yaratdığı namizəd yolları (sıra ilə sınanır). */
const LOCAL_EXTENSIONS = ["png", "svg", "webp", "jpg"] as const;

export interface LogoSource {
  /** <img src> üçün istifadə olunan dəyər */
  src: string;
  /** nəzarət etmək üçün mənbə növü */
  kind: "remote" | "local";
}

function isAbsolute(value: string): boolean {
  return /^https?:\/\//i.test(value);
}

/**
 * Verilən ad/URL üçün sınanacaq mənbələrin siyahısını qaytarır.
 * Boş dəyər verilsə, lokal fayllardan başlayan siyahı qaytarılır.
 */
export function logoCandidates(
  nameOrLogo: string | null | undefined,
  kind: LogoKind = "teams",
): LogoSource[] {
  const candidates: LogoSource[] = [];
  const raw = (nameOrLogo ?? "").trim();
  // Təkrar sınanmasın
  const push = (src: string, k: "remote" | "local") => {
    if (!candidates.some((c) => c.src === src)) candidates.push({ src, kind: k });
  };

  if (raw) {
    if (isAbsolute(raw)) {
      push(raw, "remote");
    } else {
      push(raw, "local");

      // backend/services.py yolları `/logos/leagues/*.svg` yazır,
      // frontend isə `/imgs/logos/leagues/` altından verir — burada
      // eyni faylı yenidən sınayırız.
      const legacy = raw.match(/^\/logos\/(teams|leagues)\/(.+?)(\.[a-z0-9]+)?$/i);
      if (legacy) {
        const file = legacy[2];
        push(`/imgs/logos/${legacy[1].toLowerCase()}/${file}.png`, "local");
      }
    }
  }

  // Lokal fayllar — ad və ya yolun özündən slug
  const slug = slugify(raw || "");
  if (slug) {
    for (const ext of LOCAL_EXTENSIONS) {
      push(`/imgs/logos/${kind}/${slug}.${ext}`, "local");
    }
  }

  return candidates;
}

/** LeagueConfig.logo boş olduqda LEAGUE_SLUGS fallback (services.py ilə eyni adlar). */
export const LEAGUE_LOGO_FALLBACK: Record<string, string> = {
  PL: "premier_league",
  LaLiga: "laliga",
  BL: "bundesliga",
  SA: "serie-a",
  L1: "ligue-1",
  ED: "eredivisie",
  Brasileirao: "brasileirao",
  PrimL: "primeira-liga",
  PriD: "primera-division",
  ProL: "belgian-pro-league",
  SL: "super-lig",
  EFL: "efl-championship",
  SPL: "saudi-pro-league",
  MLS: "mls",
  CFL: "czech-first-league",
  SLG: "super-league-greece",
  LPE: "liga-pro-ecuador",
  DSL: "danish-superliga",
  EKS: "ekstraklasa",
  J1L: "j1-league",
  ELI: "eliteserien",
  CSL: "chinese-super-league",
  ML: "meistriliiga",
  VL: "vysheyshaya-liga",
  SLQ: "super-liqa",
};
