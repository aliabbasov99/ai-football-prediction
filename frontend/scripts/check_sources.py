"""
Loqo mənbələrinin sağlamlıq yoxlaması.

TheSportsDB və Wikipedia mənbələrinin işləyib-işləmədiyini bilmək üçün
bir neçe komanda üçün hər iki mənbəni sınayır.

İstifadə:
    python scripts/check_sources.py                 # 5 komanda, 5 liqa
    python scripts/check_sources.py "Real Madrid"   # tək komanda
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import fetch_logos as F  # noqa: E402

DEFAULT_CASES = [
    ("England - Premier League", "Bournemouth"),
    ("Spain - LaLiga", "Celta Vigo"),
    ("Turkey - Super Lig", "Kayserispor"),
    ("Japan - J1 League", "Cerezo Osaka"),
    ("Brazil - Serie A", "Fortaleza"),
]

WIKI_LANGS = ("en", "es", "tr", "pt", "ja", "de", "it", "fr", "nl", "ru", "pl", "ar")


def check_team(fetcher: F.Fetcher, folder: str, team: str) -> None:
    meta = F.LEAGUES[folder]
    country = meta["country"]

    cands = fetcher.tsdb_search(team)
    picked = fetcher.pick_team(cands, team, country) if cands else None
    data = None
    if picked:
        data = fetcher.fetch_bytes(picked["strBadge"])
        if data:
            print(
                f"  tsdb  {team:18s} -> {picked['strTeam']:24s} "
                f"{len(data):>7} b   ({picked.get('strCountry')})",
                flush=True,
            )
        else:
            print(f"  tsdb  {team:18s} -> badge endirila bilmadi", flush=True)
    else:
        print(f"  tsdb  {team:18s} -> tapilmadi ({len(cands)} namize)", flush=True)

    if data:
        return

    for lang in WIKI_LANGS:
        wiki = fetcher.wiki_team_image(team, country, lang)
        if wiki:
            print(f"  wiki  {team:18s} -> [{lang}] {len(wiki):>7} b", flush=True)
            return
    print(f"  wiki  {team:18s} -> tapilmadi", flush=True)


def check_leagues(fetcher: F.Fetcher) -> None:
    missing = []
    for slug, folder in F.LEAGUE_SLUG_LOOKUP.items():
        if not (F.LEAGUE_DIR / f"{slug}.png").exists():
            missing.append(slug)
    total = len(F.LEAGUE_SLUG_LOOKUP)
    print(f"  liqalar: {total - len(missing)}/{total} movcud")
    if missing:
        print("  çatışmayan:", ", ".join(missing))


def main() -> int:
    if len(sys.argv) > 1:
        name = " ".join(sys.argv[1:])
        folder = next(
            (f for f, m in F.LEAGUES.items() if any(
                name.lower() == str(e).lower() or
                (isinstance(e, tuple) and name.lower() in e[0].lower())
                for e in m["teams"]
            )),
            "England - Premier League",
        )
        cases = [(folder, name)]
    else:
        cases = DEFAULT_CASES

    fetcher = F.Fetcher(workers=2)
    try:
        print("KOMANDALAR")
        for folder, team in cases:
            check_team(fetcher, folder, team)
        print("\nLIQALAR")
        check_leagues(fetcher)
    finally:
        fetcher.close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
