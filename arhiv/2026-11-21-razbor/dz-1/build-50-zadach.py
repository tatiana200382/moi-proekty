"""Собирает 50 задач в Word: 50-zadach.docx. Источник — 50-zadach.md."""

import re
from docx import Document
from docx.shared import Pt, Cm, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml.ns import qn
from docx.oxml import OxmlElement

SRC = "50-zadach.md"
OUT = "50-zadach.docx"


def shade(cell, color="EDEDED"):
    tc_pr = cell._tc.get_or_add_tcPr()
    shd = OxmlElement("w:shd")
    shd.set(qn("w:val"), "clear")
    shd.set(qn("w:color"), "auto")
    shd.set(qn("w:fill"), color)
    tc_pr.append(shd)


def fix_layout(t, widths):
    tbl_pr = t._tbl.tblPr
    layout = OxmlElement("w:tblLayout")
    layout.set(qn("w:type"), "fixed")
    tbl_pr.append(layout)
    for i, w in enumerate(widths):
        t.columns[i].width = Cm(w)
    for row in t.rows:
        tr_pr = row._tr.get_or_add_trPr()
        tr_pr.append(OxmlElement("w:cantSplit"))
        for i, w in enumerate(widths):
            row.cells[i].width = Cm(w)
    t.rows[0]._tr.get_or_add_trPr().append(OxmlElement("w:tblHeader"))


def table(doc, headers, rows, widths, size=10):
    t = doc.add_table(rows=1, cols=len(headers))
    t.style = "Table Grid"
    t.alignment = WD_TABLE_ALIGNMENT.CENTER
    t.autofit = False
    for i, h in enumerate(headers):
        c = t.rows[0].cells[i]
        c.text = ""
        r = c.paragraphs[0].add_run(h)
        r.bold = True
        r.font.size = Pt(size)
        shade(c)
    for row in rows:
        cells = t.add_row().cells
        for i, v in enumerate(row):
            cells[i].text = ""
            r = cells[i].paragraphs[0].add_run(str(v))
            r.font.size = Pt(size)
    fix_layout(t, widths)
    return t


def para(doc, text="", size=11, bold=False, italic=False, after=4, style=None):
    p = doc.add_paragraph(style=style)
    if text:
        r = p.add_run(text)
        r.font.size = Pt(size)
        r.bold = bold
        r.italic = italic
    p.paragraph_format.space_after = Pt(after)
    return p


doc = Document()
for s in doc.sections:
    s.top_margin = Cm(1.8)
    s.bottom_margin = Cm(1.8)
    s.left_margin = Cm(2)
    s.right_margin = Cm(2)
normal = doc.styles["Normal"]
normal.font.name = "Calibri"
normal.font.size = Pt(11)
normal.element.rPr.rFonts.set(qn("w:eastAsia"), "Calibri")

src = open(SRC, encoding="utf-8").read()
groups = []
current = None
for line in src.splitlines():
    if line.startswith("## "):
        name = line[3:].strip()
        if re.match(r"^\d+\.", name):
            current = {"name": name, "items": []}
            groups.append(current)
        else:
            current = None
    elif current is not None and re.match(r"^\d+\. ", line):
        m = re.match(r"^(\d+)\. (.*)$", line)
        current["items"].append((int(m.group(1)), m.group(2)))

total = sum(len(g["items"]) for g in groups)
assert total == 50, f"ожидалось 50 задач, найдено {total}"

title = doc.add_heading("50 задач для ИИ", level=0)
para(doc, "Цветочная розница, Санкт-Петербург · три магазина · 4 ноября 2026", 10, italic=True)
para(doc, "Знак ★ — делать в первую очередь: не требует денег и запускается за неделю.", 10)

for g in groups:
    head = doc.add_heading(g["name"], level=1)
    head.paragraph_format.space_before = Pt(10)
    head.paragraph_format.space_after = Pt(2)
    for num, text in g["items"]:
        priority = text.rstrip().endswith("★")
        body = text.rstrip().rstrip("★").strip()
        p = doc.add_paragraph()
        p.paragraph_format.space_after = Pt(1)
        p.paragraph_format.left_indent = Cm(0.6)
        p.paragraph_format.first_line_indent = Cm(-0.6)
        r = p.add_run(f"{num}. ")
        r.bold = True
        p.add_run(body)
        if priority:
            star = p.add_run("  ★")
            star.bold = True

doc.add_page_break()
doc.add_heading("Пять приоритетных из 50", level=1)
table(doc, ["Задача", "Влияние", "Простота", "Итог"], [
    ["2 + 3. Карточки Яндекс.Бизнеса и Google Карт", "4", "5", "20"],
    ["1. Контент-завод: букет дня и посты", "4", "4", "16"],
    ["37. Сводка дня из фото журналов", "3", "5", "15"],
    ["11. Своя база клиентов при покупке", "4", "3", "12"],
    ["29. Аналитика заказов срезки к праздникам", "5", "2", "10"],
], widths=[9.6, 2.4, 2.4, 2.4], size=10)

doc.add_heading("Что оставляем фантазией", level=1)
for t in [
    "Приложение (7) и сайт (6) — пока нет онлайн-потока: установят и откроют единицы.",
    "Боты-рассылки (9) — только вместе с CRM и своей базой.",
    "Реклама (4) — только когда видно, откуда пришла заявка.",
    "Парсинг чужих баз — персональные данные без согласия, нарушение закона. Замена — пункт 11: своя база с согласием на рассылку.",
]:
    para(doc, t, 10, style="List Bullet")

doc.add_heading("Первые три шага", level=1)
for t in [
    "Карточки в Google Картах и Яндекс.Бизнесе — сегодня-завтра, бесплатно.",
    "Сфотографировать журнал и получить первую строку в таблице — сегодня.",
    "Начать собирать базу при покупке по карте — с этой недели.",
]:
    para(doc, t, 10, style="List Number")

doc.save(OUT)
print("saved", OUT, "groups:", len(groups))
