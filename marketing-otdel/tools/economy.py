#!/usr/bin/env python3
"""economy.py — экономика заявки и акции. Только стандартная библиотека.

Примеры:
  python3 economy.py --spend 5000 --leads 20 --orders 6 --check 2500 --margin 55
  python3 economy.py --discount 10 --check 2500 --margin 55
  python3 economy.py --budget 5000 --cpl 300 --check 2500 --margin 55
"""
import argparse
import sys


def money(x):
    return f"{x:,.0f} ₽".replace(",", " ")


def main():
    p = argparse.ArgumentParser(description="Расчёт CPL, CPA, ROMI и скидки")
    p.add_argument("--spend", type=float, default=0, help="расход на канал, ₽")
    p.add_argument("--leads", type=float, default=0, help="заявки")
    p.add_argument("--orders", type=float, default=0, help="заказы")
    p.add_argument("--revenue", type=float, default=None, help="выручка, ₽ (по умолчанию orders × чек)")
    p.add_argument("--check", type=float, default=2500, help="средний чек, ₽")
    p.add_argument("--margin", type=float, default=55, help="валовая маржа, %%")
    p.add_argument("--discount", type=float, default=None, help="скидка, %% — посчитать потерю маржи")
    p.add_argument("--budget", type=float, default=None, help="бюджет, ₽ — сколько заявок при цели CPL")
    p.add_argument("--cpl", type=float, default=300, help="целевая цена заявки, ₽")
    a = p.parse_args()

    check = a.check
    gross = check * a.margin / 100.0

    if a.discount is not None:
        cut = check * a.discount / 100.0
        left = gross - cut
        print("=== Скидка ===")
        print(f"Чек: {money(check)}, маржа {a.margin:.0f}% = {money(gross)}")
        print(f"Скидка {a.discount:.0f}%: −{money(cut)} ({(cut / gross * 100 if gross else 0):.1f}% маржи)")
        print(f"Остаётся маржи: {money(left)} ({(left / check * 100):.1f}% чека)")
        need = gross / left if left > 0 else float("inf")
        print(f"Чтобы не потерять прибыль, продаж нужно больше в {need:.2f} раза")
        return

    if a.budget is not None:
        print("=== Сколько заявок на бюджет ===")
        print(f"Бюджет {money(a.budget)} ÷ CPL {money(a.cpl)} = {a.budget / a.cpl:.1f} заявок")
        print(f"При конверсии 30% это {a.budget / a.cpl * 0.3:.1f} заказов")
        print(f"Порог окупаемости по марже: CPL ≤ {money(gross * 0.3)} (30% маржи с заказа)")
        return

    if not a.spend and not a.leads:
        p.print_help()
        print("\nУкажи хотя бы --spend или --budget.")
        sys.exit(2)

    revenue = a.revenue if a.revenue is not None else a.orders * check
    cpl = a.spend / a.leads if a.leads else None
    cpa = a.spend / a.orders if a.orders else None
    cr = a.orders / a.leads * 100 if a.leads else None
    romi = (revenue - a.spend) / a.spend * 100 if a.spend else None
    margin_money = revenue * a.margin / 100.0

    print("=== Канал ===")
    print(f"Расход: {money(a.spend)} | Заявки: {a.leads:.0f} | Заказы: {a.orders:.0f} | Выручка: {money(revenue)}")
    if cpl is not None:
        print(f"CPL: {money(cpl)} {'✅' if cpl <= 300 else '❌'} (порог 300 ₽)")
    if cpa is not None:
        print(f"CPA: {money(cpa)}")
    if cr is not None:
        print(f"Конверсия заявка→заказ: {cr:.1f}%")
    if romi is not None:
        print(f"ROMI: {romi:.0f}%")
    print(f"Маржа с выручки: {money(margin_money)}; после рекламы: {money(margin_money - a.spend)}")
    if cpl is not None and cpl > 300:
        print("Вывод: дорого. Меняем аудиторию/оффер или выключаем канал.")


if __name__ == "__main__":
    main()
