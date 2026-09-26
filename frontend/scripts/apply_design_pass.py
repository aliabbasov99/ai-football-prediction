"""
Dizayn keçidi: aqressiv tipografiya və səhv kontrastlı düymələri
yumşaldır. globals.css tokenləri artıq Zinc + Zümrüd palitrasındadır;
bu ssenari qalan "font-bold" / "text-white" qalıqlarını təmizləyir.

Qeyd: ssenari yalnız LİTERAL dəyişikliklər edir, faylın UTF-8 kodlaşmasını
qoruyur (PowerShell-in here-string ilə Azərbaycan hərfləri pozulur).
"""

import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1] / "src"

# Sıra vacibdir: daha uzun/məxsus olanlar əvvəl tətbiq olunur.
RULES: list[tuple[str, str]] = [
    # ── Səhifə başlıqları ──
    ("text-2xl font-bold tracking-tight", "text-2xl font-semibold tracking-tight"),
    ("text-2xl font-bold", "text-2xl font-semibold"),
    ("text-lg font-bold", "text-lg font-semibold"),
    # ── Bölmə başlıqları ──
    ("text-sm font-bold", "text-sm font-semibold"),
    # ── Mikro etiketlər (uppercase) ──
    ("font-bold uppercase tracking-wide", "font-semibold uppercase tracking-wider"),
    ("uppercase tracking-wide", "uppercase tracking-wider"),
    # ── Rəqəmsal vurğu (tabular) ──
    ("tabular-nums font-bold", "tabular-nums font-semibold"),
    ("text-xs font-bold tabular-nums", "text-xs font-semibold tabular-nums"),
    # ── Monogram ──
    ("font-bold select-none", "font-semibold select-none"),
    # ── Ümumi fallback ──
    ("font-bold", "font-semibold"),
]

# Dolu zümrüd düymədə ağ mətn kontrasıtı zəifdir (ağ/emerald-500 ≈ 2.5:1).
# Tünd mətn (zinc-950) ≈ 8:1 — WCAG AA keçir.
COLOR_RULES: list[tuple[str, str]] = [
    (
        "bg-brand px-3 py-2 text-sm font-semibold text-white",
        "btn btn-primary",
    ),
    ('"bg-brand text-white"', '"bg-brand text-base"'),
]


def main() -> int:
    changed: list[tuple[str, int]] = []

    for path in sorted(ROOT.rglob("*.tsx")):
        src = path.read_text(encoding="utf-8")
        out = src

        for old, new in RULES:
            out = out.replace(old, new)
        for old, new in COLOR_RULES:
            out = out.replace(old, new)

        if out != src:
            path.write_text(out, encoding="utf-8")
            n = sum(1 for a, b in zip(src.splitlines(), out.splitlines()) if a != b)
            changed.append((str(path.relative_to(ROOT)), n))

    if not changed:
        print("Deyisiklik yoxdur.")
        return 0

    total = sum(n for _, n in changed)
    for f, n in changed:
        print(f"  {n:>3}  {f}")
    print(f"\n{len(changed)} fayl, {total} sətir.")

    # Qalan qalıqları göstər
    leftovers: list[str] = []
    for path in sorted(ROOT.rglob("*.tsx")):
        for i, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
            if "font-bold" in line or "text-white" in line or "rounded-3xl" in line:
                leftovers.append(f"{path.relative_to(ROOT)}:{i}: {line.strip()}")

    if leftovers:
        print(f"\nQalan {len(leftovers)} yer:")
        for l in leftovers:
            print("  " + l)
    else:
        print("\nfont-bold / text-white / rounded-3xl qalmadi.")

    # Gradient/parlaq kuklə yoxlaması
    banned = []
    for path in sorted(ROOT.rglob("*.ts*")):
        for i, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
            if re.search(r"gradient|shadow-(xl|2xl|inner|md|lg)", line):
                banned.append(f"{path.relative_to(ROOT)}:{i}: {line.strip()}")

    if banned:
        print(f"\nQadağan klasslara rast gəldim ({len(banned)}):")
        for b in banned:
            print("  " + b)
    else:
        print("gradient / kuklə yoxdur.")

    return 0


if __name__ == "__main__":
    sys.exit(main())
