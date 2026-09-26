"""
Loqo bütövlüyünü yoxlayır — `fetch_logos.py` icrasından sonra işə salın.

Yoxlananlar:
  1. Bütün fayllar REAL şəkil mi (magic bytes: PNG / JPEG / WebP / SVG)
  2. 25 liqa loqosunun hamısı varmı
  3. `src/lib/logo.ts` -> `LEAGUE_LOGO_FALLBACK` xəritəsi disklə uyğunlaşır mı
     (slug dəyişib və frontend səhifələrdə 404 görünə bilər)
  4. Fərqli liqalar bir-birinin loqosunu istifadə etmir
  5. Roosterdəki hər komandanın loqosu varmı

Çıxış kodu: 0 = xəta yoxdur, 1 = problem var.

İstifadə:
    python scripts/verify_logos.py
"""
from __future__ import annotations

import hashlib
import json
import re
import sys
from collections import defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from logos_data import LEAGUE_SLUG_LOOKUP, LEAGUES, expand  # noqa: E402
from fetch_logos import slugify  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
LOGO_ROOT = ROOT / "public" / "imgs" / "logos"
LEAGUE_DIR = LOGO_ROOT / "leagues"
TEAM_DIR = LOGO_ROOT / "teams"
LOGO_TS = ROOT / "src" / "lib" / "logo.ts"

EXTS = ("png", "svg", "webp", "jpg")

# İç içə qovluq: "{Country} - {League}/{Team}.png"
NESTED_RE = re.compile(r"^[^\\]+\\([^\\]+)\\[^\\]+$")

errors: list[str] = []
warnings: list[str] = []


def fail(msg: str) -> None:
    errors.append(msg)


def warn(msg: str) -> None:
    warnings.append(msg)


def is_image(data: bytes) -> bool:
    if data[:8] == b"\x89PNG\r\n\x1a\n":
        return True
    if data[:3] == b"\xff\xd8\xff":
        return True
    if data[:4] == b"RIFF" and data[8:12] == b"WEBP":
        return True
    head = data[:80].lstrip()
    return head.startswith(b"<svg") or head.startswith(b"<?xml")


def has(base: Path, stem: str) -> bool:
    return any((base / f"{stem}.{e}").exists() for e in EXTS)


# ── 1. Bütün fayllar real şəkil mi ────────────────────────────────────────
all_files = sorted(
    p for p in LOGO_ROOT.rglob("*") if p.is_file() and p.suffix.lstrip(".").lower() in EXTS
)
corrupt: list[str] = []
for p in all_files:
    try:
        if not is_image(p.read_bytes()):
            corrupt.append(p.relative_to(LOGO_ROOT).as_posix())
    except OSError as exc:
        corrupt.append(f"{p.relative_to(LOGO_ROOT).as_posix()} ({exc})")

print(f"Fayllar: {len(all_files)}")
if corrupt:
    fail(f"{len(corrupt)} fayl şəkil deyil: {', '.join(corrupt[:8])}")
else:
    print("  hər fayl etibarlı PNG/JPEG/WebP/SVG-dir")

# ── 2. Liqa loqoları ──────────────────────────────────────────────────────
missing = [s for s in LEAGUE_SLUG_LOOKUP if not has(LEAGUE_DIR, s)]
print(f"\nLiqa loqoları: {len(LEAGUE_SLUG_LOOKUP) - len(missing)}/{len(LEAGUE_SLUG_LOOKUP)}")
if missing:
    fail(f"çatışmayan liqa loqoları: {', '.join(missing)}")

# ── 3. LEAGUE_LOGO_FALLBACK xəritəsi disklə uyğunlaşır mı ──────────────────
if not LOGO_TS.exists():
    fail(f"{LOGO_TS} tapılmadı")
else:
    src = LOGO_TS.read_text(encoding="utf-8")
    m = re.search(r"LEAGUE_LOGO_FALLBACK[^=]*=\s*\{(.*?)\n\};", src, re.S)
    if not m:
        fail("logo.ts-də LEAGUE_LOGO_FALLBACK tapılmadı")
    else:
        fb = dict(re.findall(r"(\w+):\s*\"([^\"]+)\"", m.group(1)))
        broken = [f"{k}->{v}" for k, v in sorted(fb.items()) if not has(LEAGUE_DIR, v)]
        print(f"\nLEAGUE_LOGO_FALLBACK: {len(fb)} açar")
        if broken:
            fail(f"xəritədə faylı olmayan slug-lar: {', '.join(broken)}")
        else:
            print("  hər açar mövcud fayla uyğun gəlir")

        unknown = sorted(set(fb.values()) - set(LEAGUE_SLUG_LOOKUP))
        if unknown:
            warn(f"xəritədə `logos_data.py`-də olmayan slug-lar: {', '.join(unknown)}")

# ── 4. Fərqli liqalar eyni loqonu istifadə etmir ─────────────────────────
# "Liqa" yalnız iç içə qovluqlar üçün sayılır; `teams/` və `leagues/`
# bizim şemalarımızdır, onlar arasında təsadüfi uyğunluq problem deyil.
by_hash: dict[str, list[str]] = defaultdict(list)
for p in all_files:
    rel = p.relative_to(LOGO_ROOT).as_posix()
    by_hash[hashlib.md5(p.read_bytes()).hexdigest()].append(rel)

cross: list[list[str]] = []
for group in by_hash.values():
    if len(group) < 2:
        continue
    leagues = {m.group(1) for m in (NESTED_RE.match(x) for x in group) if m}
    if len(leagues) > 1:
        cross.append(sorted(group))

dup_groups = sum(1 for v in by_hash.values() if len(v) > 1)
print(f"\nTəkrarlar: {dup_groups} qrup")
if cross:
    for grp in cross[:5]:
        fail("fərqli liqalar eyni loqonu paylaşır: " + " | ".join(grp))
else:
    print("  fərqli liqa qovluqları arasında təkrar yoxdur")
    print("  (eyni komandaların alias slug-ları təkrar yazılır — bu gözlənilir)")

# ── 5. Komanda loqoları ───────────────────────────────────────────────────
teams = [p for p in TEAM_DIR.glob("*") if p.is_file() and p.suffix.lstrip(".").lower() in EXTS]

expected: set[str] = set()
for meta in LEAGUES.values():
    for entry in meta["teams"]:
        # `expand()` -> (ad, [alias-lar])
        name, aliases = expand(entry)
        for variant in [name, *aliases]:
            slug = slugify(variant)
            if slug:
                expected.add(slug)

covered = {p.stem for p in teams}
missing_teams = sorted(expected - covered)

print(f"\nKomanda loqoları: {len(teams)} fayl")
print(f"  roster: {len(expected & covered)}/{len(expected)} unikal slug tapıldı")
if missing_teams:
    tail = " ..." if len(missing_teams) > 12 else ""
    print(f"  çatışmayan: {len(missing_teams)}")
    print(f"    {', '.join(missing_teams[:12])}{tail}")
    warn(
        f"{len(missing_teams)}/{len(expected)} komanda üçün fayl yoxdur — "
        "həmin komandalar monogram göstərəcək"
    )
else:
    print("  bütün komanda loqoları mövcuddur")

manifest_path = LOGO_ROOT / "manifest.json"
if manifest_path.exists():
    mf = json.loads(manifest_path.read_text(encoding="utf-8"))
    resolved = len(mf.get("teams_ok", []))
    unresolved = len(mf.get("unresolved", []))
    print(f"  manifest ({mf.get('saved_at', '?')}): {resolved} həll, {unresolved} unresolved")
    if unresolved > len(missing_teams):
        warn(
            f"manifest daha çox unresolved göstərir ({unresolved}) — "
            "yükləmə bitməmiş ola bilər"
        )
else:
    warn("manifest.json yoxdur — yükləmə bitməmiş ola bilər")

# ── Yekun ─────────────────────────────────────────────────────────────────
print()
for w in warnings:
    print(f"  ! {w}")
if errors:
    for e in errors:
        print(f"  X {e}")
    print(f"\nNƏTİCƏ: {len(errors)} xəta, {len(warnings)} xəbərdarlıq")
    raise SystemExit(1)

print(f"NƏTİCƏ: xəta yoxdur ({len(warnings)} xəbərdarlıq)")
raise SystemExit(0)
