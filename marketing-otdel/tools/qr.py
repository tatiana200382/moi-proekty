#!/usr/bin/env python3
"""qr.py — QR-код с подписью для зала и витрин.

  python3 tools/qr.py --url "https://vk.me/s_sflowers?utm_source=zal" --out results/qr-zal.png
  python3 tools/qr.py --url ... --out ... --caption "Напишите нам — соберём букет"

Нужен segno (в tools/vendor) и Pillow (встроенный Python).
"""
import argparse
import pathlib
import sys

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE / "vendor"))

try:
    import segno
except ImportError:
    sys.exit("нет segno: pip install --target tools/vendor segno")


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--url", required=True)
    p.add_argument("--out", required=True)
    p.add_argument("--caption", default="Напишите нам в ВК — подберём букет к поводу")
    p.add_argument("--sub", default="Фото до отправки · замена при получении")
    a = p.parse_args()

    out = pathlib.Path(a.out)
    out.parent.mkdir(parents=True, exist_ok=True)

    qr = segno.make(a.url, error="h")
    tmp = out.with_suffix(".qr.png")
    qr.save(tmp, scale=14, border=2, dark="#3E4032", light="#FFFFFF")

    try:
        from PIL import Image, ImageDraw, ImageFont
    except ImportError:
        bundled = pathlib.Path.home() / ".dsh/dsh-runtimes/dsh-primary-runtime/dependencies/python/bin/python3"
        if bundled.exists():
            import os
            os.execv(str(bundled), [str(bundled), __file__, *sys.argv[1:]])
        tmp.replace(out)
        print("готово (без подписи):", out)
        return

    q = Image.open(tmp).convert("RGB")
    W = 1200
    QS = W - 160
    q = q.resize((QS, QS), Image.LANCZOS)
    card = Image.new("RGB", (W, 70 + QS + 170), "#FBF3EA")
    card.paste(q, (80, 70))

    draw = ImageDraw.Draw(card)

    def load(size):
        try:
            return ImageFont.truetype("/System/Library/Fonts/Supplemental/Georgia.ttf", size)
        except Exception:
            return ImageFont.load_default()

    def width(text, font):
        box = draw.textbbox((0, 0), text, font=font)
        return box[2] - box[0]

    def fit(text, size, limit):
        font = load(size)
        while width(text, font) > limit and size > 20:
            size -= 2
            font = load(size)
        return font

    f1 = fit(a.caption, 46, W - 80)
    f2 = fit(a.sub, 30, W - 80)

    def center(text, font, y, color="#3E4032"):
        draw.text(((W - width(text, font)) / 2, y), text, font=font, fill=color)

    center(a.caption, f1, 70 + QS + 30)
    center(a.sub, f2, 70 + QS + 95, "#8D9D76")
    card.save(out, "PNG")
    tmp.unlink(missing_ok=True)
    print("готово:", out)


if __name__ == "__main__":
    main()
