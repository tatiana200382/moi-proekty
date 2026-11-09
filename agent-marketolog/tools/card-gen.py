#!/usr/bin/env python3
"""Генератор карточек из CSV в трёх форматах — наш аналог Canva Magic Resize + Bulk Create.

CSV: название;цена;подпись;фото
Пример: python3 tools/card-gen.py products.csv results/karty
"""
import csv, os, sys
from PIL import Image, ImageDraw, ImageFont, ImageFilter

CREAM=(251,243,234); INK=(62,64,50); GREY=(138,133,120); SAGE=(141,157,118)
SER="/System/Library/Fonts/Supplemental/Georgia.ttf"
SANS="/System/Library/Fonts/Supplemental/Arial.ttf"
PRICE_FONT="/System/Library/Fonts/HelveticaNeue.ttc"

FORMATS = {"4x5": (1080,1350), "9x16": (1080,1920), "1x1": (1080,1080)}

def cover(im, w, h, align_right=True):
    k = max(w/im.size[0], h/im.size[1])
    im = im.resize((int(im.size[0]*k)+1, int(im.size[1]*k)+1), Image.LANCZOS)
    l = (im.size[0]-w) if align_right else (im.size[0]-w)//2
    t = (im.size[1]-h)//2
    return im.crop((l,t,l+w,t+h))

def wrap(d, text, font, maxw):
    words = text.split(); lines=[]; cur=""
    for w in words:
        t = (cur+" "+w).strip()
        if d.textlength(t, font=font) <= maxw: cur = t
        else: lines.append(cur); cur = w
    if cur: lines.append(cur)
    return lines

def card(title, price, note, photo, out, fmt):
    W,H = FORMATS[fmt]
    c = Image.new("RGB",(W,H),CREAM)
    pad = int(W*0.059)
    d = ImageDraw.Draw(c)
    f_brand = ImageFont.truetype(SANS, max(20,int(W*0.021)))
    d.text((pad, int(pad*0.4)), "SILVER SONG FLOWERS", font=f_brand, fill=GREY)

    ph = int(W*{"4x5":0.72,"9x16":1.18,"1x1":0.60}[fmt])
    y = int(pad*0.4) + int(W*0.04)
    if os.path.exists(photo):
        src = Image.open(photo).convert("RGB")
        if fmt == "9x16":
            bw, bh = W-pad*2, ph
            bg = cover(src, bw, bh).filter(ImageFilter.GaussianBlur(40))
            bg = Image.blend(bg, Image.new("RGB",(bw,bh),CREAM), 0.35)
            k = bw/src.size[0]
            fg = src.resize((bw, int(src.size[1]*k)), Image.LANCZOS)
            c.paste(bg,(pad,y))
            c.paste(fg,(pad, y+(bh-fg.size[1])//2))
        else:
            c.paste(cover(src, W-pad*2, ph),(pad,y))
    else:
        d.rectangle((pad,y,W-pad,y+ph), fill=(225,220,212))

    y += ph + int(H*0.03)
    f_t = ImageFont.truetype(SER, max(38,int(W*0.056)))
    for line in wrap(d, title, f_t, W-pad*2)[:2]:
        d.text((pad,y),line,font=f_t,fill=INK); y += int(W*0.06)
    y += int(H*0.008)
    f_p = ImageFont.truetype(PRICE_FONT, max(34,int(W*0.048)))
    d.text((pad,y), price, font=f_p, fill=INK); y += int(W*0.062)
    f_n = ImageFont.truetype(SANS, max(20,int(W*0.023)))
    for line in wrap(d, note, f_n, W-pad*2)[:2]:
        d.text((pad,y),line,font=f_n,fill=(92,95,79)); y += int(W*0.03)

    # плашка и подвал
    f_c = ImageFont.truetype(SANS, max(22,int(W*0.026)))
    t = "Написать нам"; tw = d.textlength(t, font=f_c)
    by = H - pad - int(H*0.085)
    d.rounded_rectangle((pad, by, pad+tw+int(W*0.06), by+int(H*0.05)), radius=int(H*0.025), fill=SAGE)
    d.text((pad+int(W*0.03), by+int(H*0.011)), t, font=f_c, fill=CREAM)
    f_f = ImageFont.truetype(SANS, max(18,int(W*0.019)))
    d.text((pad,H-pad-int(H*0.022)),"Белышева 5/6 · Ленинский 56 · Трибуца 8",font=f_f,fill=GREY)
    c.save(out,"JPEG",quality=93)
    return out

def main():
    if len(sys.argv) < 3:
        print("использование: card-gen.py products.csv out_dir"); return
    csv_path, out_dir = sys.argv[1], sys.argv[2]
    os.makedirs(out_dir, exist_ok=True)
    n=0
    with open(csv_path, encoding="utf-8") as f:
        for i,row in enumerate(csv.DictReader(f),1):
            for fmt in FORMATS:
                out = os.path.join(out_dir, f"{i:02d}_{fmt}.jpg")
                card(row["название"], row["цена"], row.get("подпись",""), row.get("фото",""), out, fmt); n+=1
    print("готово файлов:", n)

if __name__ == "__main__":
    main()
