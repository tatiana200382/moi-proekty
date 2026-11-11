#!/usr/bin/env python3
"""utm.py — конструктор UTM-ссылок.

  python3 utm.py --base https://site.ru --source vk --medium post --campaign 2026-11 --content buket-dnya
  python3 utm.py --standard          # готовый набор ссылок по каналам
"""
import argparse
import urllib.parse

BASE = "https://kladovaja-tsvetov-ssflowers.clients.site/"


def build(base, source, medium, campaign, content=""):
    q = {"utm_source": source, "utm_medium": medium, "utm_campaign": campaign}
    if content:
        q["utm_content"] = content
    sep = "&" if "?" in base else "?"
    return base + sep + urllib.parse.urlencode(q)


def standard():
    rows = [
        ("Карта Белышева", "yandex_maps", "card", "belysheva"),
        ("Карта Трибуца", "yandex_maps", "card", "tribuca"),
        ("Карта Ленинский", "yandex_maps", "card", "leninsky"),
        ("Пост ВК", "vk", "post", "post"),
        ("Сторис", "vk", "story", "story"),
        ("Авито", "avito", "listing", "buket"),
        ("Telegram", "telegram", "post", "post"),
        ("B2B-письмо", "b2b", "email", "hotel"),
    ]
    print("| Куда | Ссылка |")
    print("|---|---|")
    for name, src, med, cont in rows:
        print(f"| {name} | {build(BASE, src, med, '2026-11', cont)} |")


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--base", default=BASE)
    p.add_argument("--source")
    p.add_argument("--medium")
    p.add_argument("--campaign", default="2026-11")
    p.add_argument("--content", default="")
    p.add_argument("--standard", action="store_true")
    a = p.parse_args()
    if a.standard:
        standard()
        return
    if not (a.source and a.medium):
        p.error("нужны --source и --medium (или --standard)")
    print(build(a.base, a.source, a.medium, a.campaign, a.content))


if __name__ == "__main__":
    main()
