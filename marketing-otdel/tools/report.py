#!/usr/bin/env python3
"""report.py — недельный отчёт по каналам из data/metrics.csv.

CSV: date,channel,spend,impressions,clicks,leads,orders,revenue,source,note

Примеры:
  python3 report.py                      # весь файл
  python3 report.py --from 2026-11-04 --to 2026-11-10
  python3 report.py --out ../../sotrudniki/dana-analitika/results/otchet.md
  python3 report.py --template           # создать пустой шаблон
"""
import argparse
import csv
import datetime as dt
import pathlib
import sys

FIELDS = ["date", "channel", "spend", "impressions", "clicks", "leads", "orders", "revenue", "source", "note"]
DATA = pathlib.Path(__file__).resolve().parent.parent / "data" / "metrics.csv"


def num(v):
    if v is None or str(v).strip() == "":
        return None
    try:
        return float(str(v).replace(" ", "").replace(",", ".").replace("₽", ""))
    except ValueError:
        return None


def rub(x):
    return f"{x:,.0f} ₽".replace(",", " ") if x is not None else "—"


def load(path, dfrom=None, dto=None):
    if not path.exists():
        sys.exit(f"нет файла {path} — создай: python3 report.py --template")
    rows = []
    with path.open(encoding="utf-8") as f:
        for r in csv.DictReader(f):
            d = r.get("date", "")
            if dfrom and d < dfrom:
                continue
            if dto and d > dto:
                continue
            rows.append(r)
    return rows


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--from", dest="dfrom")
    p.add_argument("--to", dest="dto")
    p.add_argument("--out")
    p.add_argument("--template", action="store_true")
    a = p.parse_args()

    if a.template:
        DATA.parent.mkdir(parents=True, exist_ok=True)
        if DATA.exists():
            print("файл уже есть:", DATA)
            return
        with DATA.open("w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=FIELDS)
            w.writeheader()
        print("создан", DATA)
        return

    rows = load(DATA, a.dfrom, a.dto)
    if not rows:
        sys.exit("в выбранном периоде нет строк")

    ch = {}
    for r in rows:
        c = ch.setdefault(r["channel"], {"spend": 0.0, "imp": 0.0, "clicks": 0.0, "leads": 0.0, "orders": 0.0, "rev": 0.0, "notes": set()})
        for k, key in (("spend", "spend"), ("impressions", "imp"), ("clicks", "clicks"), ("leads", "leads"), ("orders", "orders"), ("revenue", "rev")):
            v = num(r.get(k))
            if v is not None:
                c[key] += v
        if r.get("note"):
            c["notes"].add(r["note"])

    today = dt.date.today().isoformat()
    out = [f"# Отчёт по каналам — {today}"]
    if a.dfrom or a.dto:
        out.append(f"Период: {a.dfrom or 'начало'} — {a.dto or 'сегодня'}.")
    out += ["", "| Канал | Расход | Показы | Клики | Заявки | Заказы | CPL | CPA | ROMI |", "|---|---|---|---|---|---|---|---|---|"]
    for name, c in sorted(ch.items()):
        cpl = c["spend"] / c["leads"] if c["leads"] else None
        cpa = c["spend"] / c["orders"] if c["orders"] else None
        romi = (c["rev"] - c["spend"]) / c["spend"] * 100 if c["spend"] and c["rev"] else None
        imp = f"{int(c['imp']):,}".replace(",", " ") if c["imp"] else "—"
        clicks = str(int(c["clicks"])) if c["clicks"] else "—"
        leads = str(int(c["leads"])) if c["leads"] else "нет данных"
        orders = str(int(c["orders"])) if c["orders"] else "нет данных"
        cpl_s = rub(cpl) if cpl else "нет данных"
        cpa_s = rub(cpa) if cpa else "нет данных"
        romi_s = f"{romi:.0f}%" if romi is not None else "нет данных"
        out.append(f"| {name} | {rub(c['spend'])} | {imp} | {clicks} | {leads} | {orders} | {cpl_s} | {cpa_s} | {romi_s} |")
    out.append("")
    out.append("## Пометки к строкам")
    for name, c in sorted(ch.items()):
        if c["notes"]:
            out.append(f"- **{name}:** " + "; ".join(sorted(c["notes"])))
    out += ["", "## Что проверить", "- Порог CPL — 300 ₽; дороже — стоп и разбор.", "- Показы/клики — из кабинетов, заявки — из бота и переписки; не смешивать.", "- «Нет данных» — это честный ноль, а не ошибка."]
    text = "\n".join(out) + "\n"

    if a.out:
        path = pathlib.Path(a.out)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")
        print("сохранено", path)
    else:
        print(text)


if __name__ == "__main__":
    main()
