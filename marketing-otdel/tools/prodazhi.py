#!/usr/bin/env python3
"""prodazhi.py — прогресс к цели «35 продаж за 7 дней».

  python3 tools/prodazhi.py
  python3 tools/prodazhi.py --goal 35 --days 7 --start 2026-11-11
"""
import argparse
import csv
import datetime as dt
import pathlib

DATA = pathlib.Path(__file__).resolve().parent.parent / "data" / "prodazhi-7-dney.csv"


def num(v):
    try:
        return float(str(v).replace(" ", "").replace(",", "."))
    except (TypeError, ValueError):
        return 0.0


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--goal", type=int, default=35)
    p.add_argument("--days", type=int, default=7)
    p.add_argument("--start", default="2026-11-11")
    a = p.parse_args()

    start = dt.date.fromisoformat(a.start)
    today = dt.date.today()
    elapsed = max(0, min(a.days, (today - start).days + 1))

    rows = list(csv.DictReader(DATA.open(encoding="utf-8"))) if DATA.exists() else []
    orders = sum(num(r.get("orders")) for r in rows)
    revenue = sum(num(r.get("revenue")) for r in rows)
    spend = sum(num(r.get("spend")) for r in rows)
    contacts = sum(num(r.get("contacts")) for r in rows)

    by = {}
    for r in rows:
        by.setdefault(r["channel"], 0.0)
        by[r["channel"]] += num(r.get("orders"))

    print(f"Цель: {a.goal} продаж за {a.days} дней (старт {a.start})")
    print(f"Сегодня: {today} — день {elapsed} из {a.days}")
    print(f"Есть: {orders:.0f} продаж · {contacts:.0f} обращений · {revenue:,.0f} ₽ выручки · {spend:,.0f} ₽ расхода".replace(",", " "))
    if contacts and orders:
        print(f"Конверсия обращение→продажа: {orders / contacts * 100:.0f}%")
    left = max(0, a.goal - orders)
    days_left = max(1, a.days - elapsed + 1)
    print(f"Осталось: {left:.0f} продаж за {days_left} дн. → нужно {left / days_left:.1f} в день")
    if elapsed and orders:
        forecast = orders / elapsed * a.days
        print(f"Прогноз к финишу при текущем темпе: {forecast:.0f} из {a.goal}")
        if forecast < a.goal:
            print("Статус: отстаём. Рычаги — ответы на обращения, продвижение Авито, QR в зале.")
        else:
            print("Статус: в графике.")
    else:
        print("Статус: продаж пока не внесено. Заполни data/prodazhi-7-dney.csv.")

    if by:
        print("\nПо каналам:")
        for ch, n in sorted(by.items(), key=lambda x: -x[1]):
            print(f"  {ch}: {n:.0f}")


if __name__ == "__main__":
    main()
