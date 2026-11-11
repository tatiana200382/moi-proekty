#!/usr/bin/env python3
"""photo.py — пакетная обработка фото букетов: кроп, размер, водяной знак.

  python3 photo.py --in fotki --out gotovye --size 1080x1350 --watermark "Silver Song Flowers"
  python3 photo.py --in fotki --out gotovye --thumb      # 400×500 превью

Требует Pillow. Если его нет в системном Python, скрипт сам подключит
библиотеки встроенного Python DeepSeek Harness.
"""
import argparse
import os
import pathlib
import sys

try:
    from PIL import Image, ImageDraw, ImageFont
except ImportError:
    bundled = pathlib.Path.home() / ".dsh/dsh-runtimes/dsh-primary-runtime/dependencies/python/bin/python3"
    if bundled.exists() and pathlib.Path(sys.executable).resolve() != bundled.resolve():
        os.execv(str(bundled), [str(bundled), __file__, *sys.argv[1:]])
    sys.exit("Pillow не найден: запусти через встроенный Python DeepSeek Harness (см. tools/README.md)")

EXTS = {".jpg", ".jpeg", ".png", ".heic", ".webp"}


def parse_size(s):
    w, h = s.lower().split("x")
    return int(w), int(h)


def fit_crop(img, size):
    tw, th = size
    ratio = max(tw / img.width, th / img.height)
    nw, nh = int(img.width * ratio + 0.5), int(img.height * ratio + 0.5)
    img = img.resize((nw, nh), Image.LANCZOS)
    left = (nw - tw) // 2
    top = (nh - th) // 2
    return img.crop((left, top, left + tw, top + th))


def watermark(img, text):
    draw = ImageDraw.Draw(img, "RGBA")
    try:
        font = ImageFont.truetype("/System/Library/Fonts/Supplemental/Georgia.ttf", max(18, img.width // 38))
    except Exception:
        font = ImageFont.load_default()
    pad = max(14, img.width // 40)
    box = draw.textbbox((0, 0), text, font=font)
    tw, th = box[2] - box[0], box[3] - box[1]
    x, y = img.width - tw - pad, img.height - th - pad * 2
    draw.text((x + 1, y + 1), text, font=font, fill=(0, 0, 0, 70))
    draw.text((x, y), text, font=font, fill=(255, 255, 255, 190))
    return img


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--in", dest="src", required=True)
    p.add_argument("--out", dest="dst", required=True)
    p.add_argument("--size", default="1080x1350")
    p.add_argument("--watermark", default="")
    p.add_argument("--thumb", action="store_true")
    a = p.parse_args()

    size = parse_size("400x500" if a.thumb else a.size)
    src, dst = pathlib.Path(a.src), pathlib.Path(a.dst)
    dst.mkdir(parents=True, exist_ok=True)
    files = [f for f in sorted(src.iterdir()) if f.suffix.lower() in EXTS]
    if not files:
        sys.exit(f"нет фото в {src}")

    done = 0
    for f in files:
        try:
            img = Image.open(f).convert("RGB")
            img = fit_crop(img, size)
            if a.watermark:
                img = watermark(img, a.watermark)
            out = dst / (f.stem + ".jpg")
            img.save(out, "JPEG", quality=90, optimize=True, progressive=True)
            done += 1
            print("ok", out.name, f"{out.stat().st_size // 1024} КБ")
        except Exception as e:
            print("пропуск", f.name, e)
    print(f"готово: {done} из {len(files)}")


if __name__ == "__main__":
    main()
