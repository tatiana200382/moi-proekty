#!/usr/bin/env python3
"""dashboard.py — автономный HTML-дашборд из data/metrics.csv (без зависимостей).

  python3 dashboard.py --out ../results/dashboard.html
"""
import argparse
import csv
import datetime as dt
import html
import pathlib

DATA = pathlib.Path(__file__).resolve().parent.parent / "data" / "metrics.csv"


def num(v):
    try:
        return float(str(v).replace(" ", "").replace(",", "."))
    except (TypeError, ValueError):
        return 0.0


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--out", default=str(pathlib.Path(__file__).resolve().parent.parent / "results" / "dashboard.html"))
    a = p.parse_args()

    rows = []
    if DATA.exists():
        with DATA.open(encoding="utf-8") as f:
            rows = list(csv.DictReader(f))

    ch = {}
    for r in rows:
        c = ch.setdefault(r["channel"], {"spend": 0, "leads": 0, "orders": 0, "clicks": 0, "imp": 0, "rev": 0})
        for k, key in (("spend", "spend"), ("leads", "leads"), ("orders", "orders"), ("clicks", "clicks"), ("impressions", "imp"), ("revenue", "rev")):
            c[key] += num(r.get(k))

    max_leads = max([c["leads"] for c in ch.values()] + [1])
    bars = []
    for name, c in sorted(ch.items(), key=lambda x: -x[1]["leads"]):
        w = int(c["leads"] / max_leads * 100)
        cpl = c["spend"] / c["leads"] if c["leads"] else 0
        bars.append(
            f'<div class="row"><span class="name">{html.escape(name)}</span>'
            f'<span class="bar"><i style="width:{max(w,1)}%"></i></span>'
            f'<span class="val">{c["leads"]:.0f} заявок · {cpl:.0f} ₽ CPL</span></div>'
        )

    table = "".join(
        f"<tr><td>{html.escape(n)}</td><td>{c['spend']:,.0f} ₽</td><td>{c['imp']:,.0f}</td><td>{c['clicks']:,.0f}</td>"
        f"<td>{c['leads']:,.0f}</td><td>{c['orders']:,.0f}</td></tr>".replace(",", " ")
        for n, c in sorted(ch.items())
    )

    now = dt.datetime.now().strftime("%d.%m.%Y %H:%M")
    doc = f"""<!doctype html><html lang="ru"><head><meta charset="utf-8">
<title>Маркетинг Silver Song — дашборд</title>
<style>
body{{font-family:-apple-system,Segoe UI,Roboto,sans-serif;background:#FBF3EA;color:#3E4032;margin:0;padding:32px}}
h1{{font-weight:600;font-size:24px;margin:0 0 4px}} .sub{{color:#7b7f6d;font-size:13px;margin-bottom:24px}}
.card{{background:#fff;border-radius:14px;padding:20px 24px;margin-bottom:18px;box-shadow:0 2px 10px rgba(62,64,50,.06)}}
.row{{display:flex;align-items:center;gap:12px;margin:10px 0;font-size:14px}}
.name{{width:170px;color:#3E4032}} .bar{{flex:1;background:#eee8df;border-radius:6px;height:14px;overflow:hidden}}
.bar i{{display:block;height:100%;background:#8D9D76}} .val{{width:220px;text-align:right;color:#7b7f6d}}
table{{width:100%;border-collapse:collapse;font-size:14px}} th,td{{padding:8px 10px;border-bottom:1px solid #f0e9df;text-align:left}}
th{{color:#7b7f6d;font-weight:500}} .warn{{color:#a05a4b}}
</style></head><body>
<h1>Маркетинг Silver Song Flowers</h1>
<div class="sub">Обновлено {now} · источник: data/metrics.csv</div>
<div class="card"><b>Заявки по каналам</b>{''.join(bars) or '<p class="warn">данных нет</p>'}</div>
<div class="card"><b>Таблица</b><table><tr><th>Канал</th><th>Расход</th><th>Показы</th><th>Клики</th><th>Заявки</th><th>Заказы</th></tr>{table or '<tr><td colspan=6 class="warn">данных нет</td></tr>'}</table></div>
<div class="card sub">Порог: CPL ≤ 300 ₽. Нет данных — не ноль, а отсутствие замера.</div>
</body></html>"""
    out = pathlib.Path(a.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(doc, encoding="utf-8")
    print("дашборд:", out)


if __name__ == "__main__":
    main()
