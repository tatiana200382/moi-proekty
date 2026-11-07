"""Генератор XML для «Авито Автозагрузки».

Собирает фид из простой таблицы товаров (CSV) по формату автозагрузки Авито.
Ничего не публикует: только пишет файл, который владелец загружает сам.

Использование:
    python3 avito-feed.py товары.csv results/avito-feed.xml
"""
import csv
import sys
from datetime import datetime, timezone
from xml.sax.saxutils import escape

HEADER = '<?xml version="1.0" encoding="UTF-8"?>'


def clean(value: str) -> str:
    return escape((value or "").strip())


def build(rows, city="Санкт-Петербург"):
    out = [HEADER, "<Ads formatVersion=\"3\" target=\"Avito.ru\">"]
    for i, row in enumerate(rows, start=1):
        title = clean(row.get("Название", ""))
        price = clean(row.get("Цена", "0"))
        desc = clean(row.get("Описание", ""))
        images = [x.strip() for x in (row.get("Фото") or "").split(";") if x.strip()]
        out.append(f"  <Ad>")
        out.append(f"    <Id>{clean(row.get('Id') or f'item-{i}')}</Id>")
        out.append(f"    <Category>{clean(row.get('Категория', 'Цветы'))}</Category>")
        out.append(f"    <GoodsType>Букеты</GoodsType>")
        out.append(f"    <Title>{title}</Title>")
        out.append(f"    <Description><![CDATA[{row.get('Описание','').strip()}]]></Description>")
        out.append(f"    <Price>{price}</Price>")
        out.append(f"    <Address>{clean(row.get('Адрес', 'Санкт-Петербург, Ленинский проспект, 56'))}</Address>")
        out.append(f"    <City>{clean(city)}</City>")
        for n, url in enumerate(images, start=1):
            out.append(f"    <Image url=\"{clean(url)}\" />")
        out.append("  </Ad>")
    out.append("</Ads>")
    return "\n".join(out)


def main():
    if len(sys.argv) < 3:
        print("нужно два файла: товары.csv и путь для XML")
        return 1
    src, dst = sys.argv[1], sys.argv[2]
    with open(src, encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    xml = build(rows)
    with open(dst, "w", encoding="utf-8") as f:
        f.write(xml)
    print(f"готово: {dst}, позиций {len(rows)}, {datetime.now(timezone.utc):%Y-%m-%d %H:%M} UTC")
    return 0


if __name__ == "__main__":
    sys.exit(main())
