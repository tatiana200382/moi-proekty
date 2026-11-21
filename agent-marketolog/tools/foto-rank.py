# -*- coding: utf-8 -*-
"""Ранжирует фото букетов по качеству: разрешение + резкость.

Использование:
    python3 tools/foto-rank.py            # топ-20
    python3 tools/foto-rank.py --all      # все, CSV в results/foto-reyting.csv
"""
from __future__ import annotations

import argparse
import csv
import pathlib
import sys

from PIL import Image, ImageFilter, ImageStat

ROOT = pathlib.Path(__file__).resolve().parent.parent
FOLDERS = [
    ROOT / "foto" / "bukety-arhiv",
    ROOT / "foto" / "media-gpt",
]
MIN_SIDE = 1200          # короткая сторона, меньше — не годится для печати и Авито
TARGET_SIDE = 1600       # желаемая короткая сторона


def sharpness(im: Image.Image) -> float:
    """Дисперия после фильтра краёв: чем выше, тем резче кадр."""
    small = im.convert("L").resize((min(im.width, 800), min(im.height, 800)))
    edges = small.filter(ImageFilter.FIND_EDGES)
    return ImageStat.Stat(edges).var[0]


def score(path: pathlib.Path) -> dict | None:
    try:
        with Image.open(path) as im:
            w, h = im.size
            sh = sharpness(im)
    except Exception:
        return None
    short = min(w, h)
    res_score = min(short / TARGET_SIDE, 1.0) * 60
    sharp_score = min(sh / 300, 1.0) * 40
    return {
        "file": str(path.relative_to(ROOT)),
        "w": w, "h": h, "short": short,
        "sharp": round(sh, 1),
        "score": round(res_score + sharp_score, 1),
        "usable": short >= MIN_SIDE,
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--all", action="store_true")
    args = ap.parse_args()

    rows = []
    for folder in FOLDERS:
        if not folder.exists():
            continue
        for p in folder.glob("**/*"):
            if p.suffix.lower() not in {".jpg", ".jpeg", ".png"}:
                continue
            r = score(p)
            if r:
                rows.append(r)
    rows.sort(key=lambda r: r["score"], reverse=True)

    good = [r for r in rows if r["usable"]]
    print(f"всего фото: {len(rows)} | годных (короткая сторона ≥ {MIN_SIDE}): {len(good)}")

    show = rows if args.all else rows[:20]
    print(f"{'#':>2} {'балл':>5} {'размер':>11} {'резкость':>8}  файл")
    for i, r in enumerate(show, 1):
        mark = "" if r["usable"] else "  ← мелкий"
        print(f"{i:>2} {r['score']:>5} {r['w']}x{r['h']:<5} {r['sharp']:>8}  {r['file']}{mark}")

    out = ROOT / "results" / "foto-reyting.csv"
    out.parent.mkdir(exist_ok=True)
    with out.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["file", "score", "w", "h", "short", "sharp", "usable"])
        w.writeheader()
        w.writerows(rows)
    print("CSV:", out.relative_to(ROOT))
    return 0


if __name__ == "__main__":
    sys.exit(main())
