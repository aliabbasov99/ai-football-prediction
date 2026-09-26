"""
Bütün komanda və liqa loqolarını yükləyir.

Mənbələr (sıra ilə):
  1. TheSportsDB `searchteams.php` (açar "3")  -> strBadge
  2. Wikipedia REST summary                      -> thumbnail (komanda üçün ehtiyat)
  3. Heç biri işləməsə: heç nə yazılmır — frontend monogram fallback göstərir
     (bozuk/placeholder şəkil heç vaxt yaranmır)

Çıxışlar (frontend/public/imgs/logos/):
  teams/{slug}.png               — frontend-in düz slug fallback zənciri
  {Country} - {League}/{Team}.png — backend/scripts/map_logos.py üçün
  leagues/{slug}.png             — liqa loqoları
  manifest.json                  — slug -> fayl xəritəsi (frontendlə təhlükəsizlik üçün)

İstifadə:
    python scripts/fetch_logos.py                # hamısı
    python scripts/fetch_logos.py --leagues      # yalnız liqa loqoları
    python scripts/fetch_logos.py --force        # mövcud faylları yenilə
    python scripts/fetch_logos.py --workers 12
"""

from __future__ import annotations

import argparse
import io
import json
import re
import sys
import threading
import time
import unicodedata
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from urllib.parse import quote

import httpx

sys.path.insert(0, str(Path(__file__).parent))
from logos_data import (  # noqa: E402
    BACKEND_SLUG_TO_FILE,
    LEAGUES,
    LEAGUE_SLUG_LOOKUP,
    expand,
)

ROOT = Path(__file__).resolve().parents[1]
LOGO_ROOT = ROOT / "public" / "imgs" / "logos"
FLAT_DIR = LOGO_ROOT / "teams"
LEAGUE_DIR = LOGO_ROOT / "leagues"

FORCE = False

TSDB_KEY = "3"
TSDB_URL = f"https://www.thesportsdb.com/api/v1/json/{TSDB_KEY}/searchteams.php"
WIKI_URL = "https://en.wikipedia.org/api/rest_v1/page/summary/{}"
UA = "afp-logo-fetch/1.0 (https://github.com/; contact: local)"

# ---------------------------------------------------------------- yardımcılar

_SLUG_RE = re.compile(r"[^a-z0-9]+")


def slugify(value: str) -> str:
    """frontend/src/lib/utils.ts slugify ilə eyni nəticə verir."""
    norm = unicodedata.normalize("NFKD", value)
    norm = "".join(c for c in norm if not unicodedata.combining(c))
    norm = norm.lower()
    return _SLUG_RE.sub("-", norm).strip("-")


def norm_name(value: str) -> str:
    """Ad müqayisəsi üçün: kiçik, söz/simvol ayrılmış."""
    norm = unicodedata.normalize("NFKD", value or "")
    norm = "".join(c for c in norm if not unicodedata.combining(c))
    return _SLUG_RE.sub(" ", norm.lower()).strip()


def is_image(data: bytes) -> bool:
    """Faylın həqiqətən şəkil olduğunu yoxlayır (SVG/PNG/JPEG/WebP)."""
    if len(data) < 200:
        return False
    head = data[:512].lstrip()
    if b"<svg" in head.lower() or data[:5] == b"<?xml":
        return b"<svg" in data[:2048].lower()
    if data.startswith(b"\x89PNG"):
        return True
    if data[:3] == b"\xff\xd8\xff":
        return True
    if data[:4] == b"RIFF" and data[8:12] == b"WEBP":
        return True
    if data[:6] in (b"GIF87a", b"GIF89a"):
        return True
    return False


# ------------------------------------------------------------------ yükləmə


class AdaptiveLimiter:
    """
    Ozun u tənzimləyən sorğu sürəti.

    Ölçmə (20 komanda, aralıqsız): ilk 20 sorğunun hamısı 200, növbəti 20-nin
    10-u 200 / 10-u boş-body 429, sonrakı 20-nin hamısı 429 -- yəni pulsuz açar
    burst + cooldown rejimində işləyir.

    Buna görə sabit interval yox: uğurlu sorğuda interval azalır,
    boş-body 429-da ikiqat artır və bütün worker-lərə cooldown tətbiq edilir.
    """

    def __init__(
        self,
        interval: float = 0.35,
        min_interval: float = 0.2,
        max_interval: float = 8.0,
    ):
        self.interval = interval
        self.min_interval = min_interval
        self.max_interval = max_interval
        self._next_at = 0.0
        self._lock = threading.Lock()
        self.throttles = 0

    def wait(self) -> None:
        with self._lock:
            now = time.monotonic()
            delay = max(0.0, self._next_at - now)
            self._next_at = max(now, self._next_at) + self.interval
        if delay > 0:
            time.sleep(delay)

    def penalize(self) -> float:
        """Bos-body 429 - yavasla, gozləmə muddətini qaytar."""
        with self._lock:
            self.interval = min(self.interval * 2, self.max_interval)
            self.throttles += 1
            return min(20.0 * self.throttles, 90.0)

    def reward(self) -> None:
        with self._lock:
            self.interval = max(self.min_interval, self.interval * 0.95)

    def cooldown(self, seconds: float) -> None:
        with self._lock:
            self._next_at = max(self._next_at, time.monotonic() + seconds)


# TheSportsDB üçün ~1.4 sorğu/saniyə (təhlükəsiz)
TSDB_LIMITER = AdaptiveLimiter()

# Wikipedia öz limiter-ini saxlayır (~3 req/s, throttle-a görə yavaşlayır)
WIKI_LIMITER = AdaptiveLimiter(interval=0.4, min_interval=0.3, max_interval=6.0)

# Sorğu nəticələrinin diski cache-i — təkrar icra 429 yaratmasın
CACHE_PATH = Path(__file__).parent / ".tsdb_cache.json"
_cache_lock = threading.Lock()
_cache: dict[str, list] = {}
# Boş nəticə də cache-lənir ki, həmin komanda üçün təkrar sorğu getməsin
_cache_empty: set[str] = set()


def cache_load() -> None:
    if not CACHE_PATH.exists():
        return
    try:
        raw = json.loads(CACHE_PATH.read_text(encoding="utf-8"))
    except Exception:
        return
    if isinstance(raw, dict):
        _cache.update(raw.get("teams", {}))
        _cache_empty.update(raw.get("empty", []))
    else:  # evvelki format
        _cache.update(raw)


def cache_save() -> None:
    with _cache_lock:
        CACHE_PATH.write_text(
            json.dumps(
                {
                    "teams": _cache,
                    "empty": sorted(_cache_empty),
                    "saved_at": time.strftime("%Y-%m-%dT%H:%M:%S"),
                },
                ensure_ascii=False,
            ),
            encoding="utf-8",
        )


class Fetcher:
    def __init__(self, workers: int = 8, timeout: float = 25.0):
        self.client = httpx.Client(
            timeout=timeout,
            follow_redirects=True,
            headers={"User-Agent": UA, "Accept": "*/*"},
            limits=httpx.Limits(max_connections=4, max_keepalive_connections=4),
        )
        self.workers = workers
        self.owns_client = True

    # -- TheSportsDB ---------------------------------------------------------
    def tsdb_search(self, query: str) -> list[dict]:
        """
        Axtarış nəticəsi.

        VACİB: pulsuz açar (key "3") limit aşıldıqda HTTP 429 qaytarır,
        amma body-də DÜZGÜN JSON məlumat olur. ona görə status kodu 200
        deyiləndə də body parse edilməyə çalışılır.
        """
        key = query.strip().lower()
        with _cache_lock:
            if key in _cache:
                return _cache[key]
            if key in _cache_empty:
                return []

        teams: list[dict] = []
        for attempt in range(6):
            TSDB_LIMITER.wait()
            try:
                r = self.client.get(TSDB_URL, params={"t": query})
            except Exception:
                time.sleep(1.0 * (attempt + 1))
                continue

            # Status koduna baxmadan body-ni oxu
            try:
                data = r.json()
            except Exception:
                data = None
            if isinstance(data, dict):
                raw = data.get("teams") or []
                parsed = [t for t in raw if isinstance(t, dict)]
                if parsed:
                    teams = parsed
                    TSDB_LIMITER.reward()
                    break
                if r.status_code == 200:
                    break

            # Bos body + 429 -> limite dustduk
            wait_s = TSDB_LIMITER.penalize()
            print(f"    [429] {query!r} - {wait_s:.0f}s", flush=True)
            TSDB_LIMITER.cooldown(wait_s)

        with _cache_lock:
            if teams:
                _cache[key] = teams
            else:
                _cache_empty.add(key)
        return teams

    def pick_team(self, candidates: list[dict], name: str, country: str) -> dict | None:
        """Ən uyğun TheSportsDB nəticəsini seçir."""
        target = norm_name(name)
        best = None
        best_score = -1

        for t in candidates:
            badge = (t.get("strBadge") or "").strip()
            if not badge or not badge.lower().endswith((".png", ".jpg", ".jpeg")):
                continue
            sport = (t.get("strSport") or "").lower()
            if sport and sport != "soccer":
                continue

            cand = norm_name(t.get("strTeam") or "")
            score = 0
            if cand == target:
                score += 100
            elif cand.startswith(target) or target.startswith(cand):
                score += 55
            elif target in cand or cand in target:
                score += 30
            else:
                # söz örtüşməsi
                a, b = set(target.split()), set(cand.split())
                if a & b:
                    score += 20 + 10 * len(a & b)

            tcountry = norm_name(t.get("strCountry") or "")
            if tcountry and tcountry == norm_name(country):
                score += 25
            elif tcountry:
                score -= 10

            if score > best_score:
                best_score, best = score, t

        # çox zəif uyğunluqda heç nə qəbul etmə
        if best_score < 30:
            return None
        return best

    # -- Wikipedia -----------------------------------------------------------
    def wiki_thumb(self, titles: str | list[str]) -> bytes | None:
        """
        Wikipedia REST summary-dən thumbnail götürür.

        Wikipedia paralel sorğuları throttle edir (429/403), ona görə:
          * hər dil üçün 3 cəhd, exponential backoff
          * 429/403 halında Retry-After-ə riayət
        """
        if isinstance(titles, str):
            titles = [titles]

        for raw_title in titles:
            path = quote(raw_title.replace(" ", "_"), safe="")
            for lang in ("en", "az", "de", "fr", "es", "pt", "ru", "nl", "pl"):
                for attempt in range(3):
                    try:
                        r = self.client.get(
                            f"https://{lang}.wikipedia.org/api/rest_v1/page/summary/{path}"
                        )
                    except Exception:
                        time.sleep(0.5 * (2**attempt))
                        continue

                    if r.status_code == 200:
                        try:
                            data = r.json()
                        except Exception:
                            break
                        thumb = (data.get("thumbnail") or {}).get("source")
                        if not thumb:
                            break
                        img = self.fetch_bytes(thumb, tries=2)
                        if img:
                            return img
                        break  # səhifə tapıldı, amma şəkil yoxdur → digər səhifə

                    if r.status_code in (429, 403, 503):
                        delay = 2.0 * (2**attempt)
                        ra = r.headers.get("Retry-After")
                        if ra and ra.isdigit():
                            delay = min(float(ra), 15.0)
                        time.sleep(delay)
                        continue

                    break  # 404 və s. → digər dil/səhifə
        return None

    def wiki_page_image(
        self,
        title: str,
        must_contain: str = "logo",
        lang: str | None = None,
    ) -> bytes | None:
        """
        Ehtiyat: summary API thumbnail verməyəndə səhifənin şəkil fayllarını
        yoxlayır (mediawiki generator=images) və uyğun faylı götürür.

        `must_contain=None` — səhifənin ilk (ən böyük) şəklini götürür.
        """
        from urllib.parse import unquote

        for lg in (lang,) if lang else ("en", "nl", "pl"):
            try:
                r = self.client.get(
                    f"https://{lg}.wikipedia.org/w/api.php",
                    params={
                        "action": "query",
                        "titles": title,
                        "generator": "images",
                        "gimlimit": "50",
                        "prop": "imageinfo",
                        "iiprop": "url|size",
                        "iiurlwidth": "320",
                        "format": "json",
                    },
                )
                if r.status_code != 200:
                    continue
            except Exception:
                continue

            pages = (r.json().get("query") or {}).get("pages") or {}
            # Əvvəlcə "logo"/"crest" adlı fayllar, sonra istənilən hər hansı
            cands = list(pages.values())
            if must_contain:
                preferred = [
                    p for p in cands
                    if must_contain in unquote(p.get("title", "")).lower()
                ]
                cands = preferred or cands
            cands.sort(key=lambda p: p.get("index", 999))

            for page in cands:
                info = (page.get("imageinfo") or [{}])[0]
                url = info.get("thumburl") or info.get("url")
                if not url:
                    continue
                data = self.fetch_bytes(url, tries=2)
                if data:
                    return data
        return None

    def wiki_search_titles(self, query: str, lang: str, limit: int = 5) -> list[str]:
        """Wikipedia axtarış API-sindən səhifə adları qaytarır."""
        try:
            r = self.client.get(
                f"https://{lang}.wikipedia.org/w/api.php",
                params={
                    "action": "query",
                    "list": "search",
                    "srsearch": query,
                    "srlimit": str(limit),
                    "format": "json",
                },
            )
            if r.status_code != 200:
                return []
            return [x["title"] for x in r.json().get("query", {}).get("search", [])]
        except Exception:
            return []

    def wiki_team_image(
        self, name: str, country: str, lang: str = "en"
    ) -> bytes | None:
        """
        Komanda loqosu üçün Wikipedia ehtiyatı.

        Addım 1: axtarış API ilə doğru səhifə adını tap.
        Addım 2: səhifənin şəkil fayllarından "logo"/"crest" olanı götür.
        """
        WIKI_LIMITER.wait()
        queries = [f'{name} football club', f"{name} {country} football"]
        titles: list[str] = []
        for q in queries:
            titles = self.wiki_search_titles(q, lang)
            if titles:
                break
        if not titles:
            return None

        for title in titles:
            WIKI_LIMITER.wait()
            data = self.wiki_page_image(title, lang=lang, must_contain=None)
            if data:
                return data
            data = self.wiki_page_image(title, lang=lang, must_contain="logo")
            if data:
                return data
        return None

    def fetch_bytes(self, url: str, tries: int = 3) -> bytes | None:
        """
        Şəkil baytlarını yükləyir.

        Status kodu 200 şərti qoyulmur: TheSportsDB limit aşılanda 429
        göndərir, amma body hələ də PNG-dir.
        """
        for attempt in range(tries):
            try:
                r = self.client.get(url)
                if is_image(r.content):
                    return r.content
            except Exception:
                pass
            time.sleep(0.4 * (attempt + 1))
        return None

    def close(self):
        self.client.close()


# --------------------------------------------------------------- komandalar


def process_team(fetcher: Fetcher, folder: str, entry, report: dict) -> None:
    name, aliases = expand(entry)
    meta = LEAGUES[folder]
    country = meta["country"]

    data: bytes | None = None
    source = ""

    # 1-ci manbe: TheSportsDB (alias-larla siraya)
    queries = [name, *aliases]
    chosen = None
    for q in queries:
        cands = fetcher.tsdb_search(q)
        if not cands:
            continue
        picked = fetcher.pick_team(cands, q, country)
        if picked:
            chosen = picked
            break

    if chosen:
        data = fetcher.fetch_bytes(chosen["strBadge"])
        if data:
            source = "tsdb:" + (chosen.get("strTeam") or "")

    # 2-ci manbe: Wikipedia (TheSportsDB tapa bilməyəndə)
    if not data:
        for lang in ("en", "es", "de", "tr", "it", "pt", "fr", "nl", "ru", "pl", "ar"):
            data = fetcher.wiki_team_image(name, country, lang)
            if data:
                source = f"wiki:{lang}"
                break

    if not data:
        report["unresolved"].append({"folder": folder, "team": name})
        return

    # 1) düz slug faylı (frontend fallback)
    flat = FLAT_DIR / f"{slugify(name)}.png"
    flat.parent.mkdir(parents=True, exist_ok=True)
    flat.write_bytes(data)

    # 2) alias variantlarının hamısı üçün düz fayl
    for extra in [name, *aliases]:
        s = slugify(extra)
        if s and s != slugify(name):
            p = FLAT_DIR / f"{s}.png"
            if not p.exists():
                p.write_bytes(data)

    # 3) map_logos.py üçün iç içə qovluq
    nested_dir = LOGO_ROOT / folder
    nested_dir.mkdir(parents=True, exist_ok=True)
    (nested_dir / f"{name}.png").write_bytes(data)

    report["teams_ok"].append(
        {
            "folder": folder,
            "team": name,
            "source": source,
            "colour": (chosen or {}).get("strColour1") or None,
        }
    )


# ----------------------------------------------------------------- liqalar


def process_league(fetcher: Fetcher, slug_file: str, folder: str, report: dict) -> None:
    meta = LEAGUES[folder]
    out = LEAGUE_DIR / f"{slug_file}.png"
    if out.exists() and not FORCE:
        report["leagues_ok"].append({"slug": slug_file, "folder": folder, "cached": True})
        return

    data = fetcher.wiki_thumb(meta["wiki"])
    if not data:
        # summary API thumbnail vermədi — səhifənin şəkil fayllarından axtar
        titles = meta["wiki"] if isinstance(meta["wiki"], list) else [meta["wiki"]]
        for t in titles:
            data = fetcher.wiki_page_image(t)
            if data:
                break
    if not data:
        report["leagues_unresolved"].append(folder)
        return

    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_bytes(data)
    report["leagues_ok"].append({"slug": slug_file, "folder": folder, "name": meta["name"]})


# --------------------------------------------------------------------- main


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--leagues", action="store_true", help="yalnız liqa loqoları")
    ap.add_argument("--teams", action="store_true", help="yalnız komanda loqoları")
    ap.add_argument("--force", action="store_true", help="mövcud faylları yenilə")
    ap.add_argument("--workers", type=int, default=10)
    ap.add_argument("--limit-leagues", type=int, default=0, help="test üçün: N liqa")
    args = ap.parse_args()

    only_leagues = args.leagues and not args.teams
    only_teams = args.teams and not args.leagues

    global FORCE
    FORCE = args.force

    LOGO_ROOT.mkdir(parents=True, exist_ok=True)
    FLAT_DIR.mkdir(parents=True, exist_ok=True)
    LEAGUE_DIR.mkdir(parents=True, exist_ok=True)

    report = {
        "teams_ok": [],
        "unresolved": [],
        "leagues_ok": [],
        "leagues_unresolved": [],
    }

    fetcher = Fetcher(workers=args.workers)
    cache_load()
    started = time.time()

    try:
        # ── Liqa loqoları ──
        if not only_teams:
            print(f"Liqa loqolari: {len(LEAGUE_SLUG_LOOKUP)}")
            # Wikipedia throttle edir — liqa loqolarını az paralelliklə çəkirik
            with ThreadPoolExecutor(max_workers=3) as pool:
                futs = {
                    pool.submit(process_league, fetcher, slug, folder, report): slug
                    for slug, folder in LEAGUE_SLUG_LOOKUP.items()
                }
                for i, f in enumerate(as_completed(futs), 1):
                    try:
                        f.result()
                    except Exception as exc:  # noqa: BLE001
                        print(f"  ! {futs[f]}: {exc}")
                    if i % 5 == 0 or i == len(futs):
                        print(f"  {i}/{len(futs)}")

        # ── Komanda loqoları ──
        if not only_leagues:
            folders = list(LEAGUES)
            if args.limit_leagues:
                folders = folders[: args.limit_leagues]

            jobs = []
            for folder in folders:
                for entry in LEAGUES[folder]["teams"]:
                    if not args.force:
                        name, _ = expand(entry)
                        if (FLAT_DIR / f"{slugify(name)}.png").exists():
                            report["teams_ok"].append(
                                {"folder": folder, "team": name, "cached": True}
                            )
                            continue
                    jobs.append((folder, entry))

            total = sum(len(LEAGUES[f]["teams"]) for f in folders)
            print(f"Komanda loqolari: {len(jobs)} yuklenecek / {total} umumi")

            with ThreadPoolExecutor(max_workers=args.workers) as pool:
                futs = {
                    pool.submit(process_team, fetcher, folder, entry, report): folder
                    for folder, entry in jobs
                }
                for i, f in enumerate(as_completed(futs), 1):
                    try:
                        f.result()
                    except Exception as exc:  # noqa: BLE001
                        print(f"  ! {futs[f]}: {exc}", flush=True)
                    if i % 10 == 0 or i == len(futs):
                        ok = len(report["teams_ok"])
                        bad = len(report["unresolved"])
                        print(
                            f"  {i}/{len(futs)}  |  temizlənmiş: {ok}  "
                            f"unresolved: {bad}  |  interval: "
                            f"{TSDB_LIMITER.interval:.2f}s  "
                            f"throttle: {TSDB_LIMITER.throttles}",
                            flush=True,
                        )
                        cache_save()
    finally:
        cache_save()
        fetcher.close()

    # ── Manifest + backend slug uyğunluğu ──────────────────────────────────
    manifest_path = LOGO_ROOT / "manifest.json"
    manifest = {
        "generated_at": time.strftime("%Y-%m-%dT%H:%M:%S"),
        "duration_sec": round(time.time() - started, 1),
        "leagues": {r["slug"]: r["folder"] for r in report["leagues_ok"]},
        "teams": {r["team"]: r.get("tsdb") for r in report["teams_ok"]},
        "unresolved": report["unresolved"],
        "leagues_unresolved": report["leagues_unresolved"],
    }
    if manifest_path.exists():
        try:
            old = json.loads(manifest_path.read_text(encoding="utf-8"))
            old_teams = old.get("teams", {})
            old_teams.update(manifest["teams"])
            manifest["teams"] = old_teams
        except Exception:
            pass
    manifest_path.write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8"
    )

    # backend/servis.py-dəki `/logos/leagues/*.png` yollarını yoxla
    alias_note = []
    for backend_slug, slug_file in BACKEND_SLUG_TO_FILE.items():
        alias_note.append(f"  {backend_slug:14s} -> /imgs/logos/leagues/{slug_file}.png")

    n_ok = len(report["teams_ok"])
    n_bad = len(report["unresolved"])
    print("\n" + "=" * 58)
    print(f"Komanda loqolari : {n_ok} temizlendi, {n_bad} unresolved")
    print(f"Liqa loqolari    : {len(report['leagues_ok'])} temizlendi, "
          f"{len(report['leagues_unresolved'])} unresolved")
    print(f"Muddet           : {manifest['duration_sec']}s")
    print(f"Manifest         : {manifest_path}")
    if report["unresolved"]:
        print("\nUnresolved komandalar:")
        for u in report["unresolved"][:40]:
            print(f"  - {u['folder']}: {u['team']}")
        if n_bad > 40:
            print(f"  ... ve {n_bad - 40} daha")
    print("\nBackend slug -> fayl:")
    for line in alias_note[:6]:
        print(line)
    print(f"  ... ({len(alias_note)} alias)")
    print("=" * 58)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
