"""Собирает проект в Word: proekt.docx."""

from docx import Document
from docx.shared import Pt, Cm
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml.ns import qn
from docx.oxml import OxmlElement


def shade(cell, color="EDEDED"):
    tc_pr = cell._tc.get_or_add_tcPr()
    shd = OxmlElement("w:shd")
    shd.set(qn("w:val"), "clear")
    shd.set(qn("w:color"), "auto")
    shd.set(qn("w:fill"), color)
    tc_pr.append(shd)


def fix_layout(t, widths):
    layout = OxmlElement("w:tblLayout")
    layout.set(qn("w:type"), "fixed")
    t._tbl.tblPr.append(layout)
    for i, w in enumerate(widths):
        t.columns[i].width = Cm(w)
    for row in t.rows:
        row._tr.get_or_add_trPr().append(OxmlElement("w:cantSplit"))
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


def h(doc, text, level=1):
    head = doc.add_heading(text, level=level)
    head.paragraph_format.space_before = Pt(12)
    head.paragraph_format.space_after = Pt(3)
    return head


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

doc.add_heading("Главный проект: первые онлайн-заказы", level=0)
para(doc, "Цветочная розница, Санкт-Петербург · три магазина · 4 ноября 2026", 10, italic=True)
para(doc, "Один проект, который можно проверить за месяц: не «сайт вообще», а поток заявок, который видно в цифрах.", 10)

h(doc, "1. Проблема и её цена")
para(doc, "Сейчас покупатели приходят с улицы: 20–40 чеков в день, а обращений в мессенджерах и по телефону — 0–3 в день. "
          "В соцсетях по 3–4 подписчика, витрины нет, реклама 5 000 ₽/мес уходит без учёта результата. Онлайн-канал продаж не приносит.")
para(doc, "Цена в деньгах: весь рост зависит от проходимости у трёх точек. Чтобы выручка выросла вдвое, нужно ещё ≈ 2,1 млн ₽ в месяц — "
          "около 840 дополнительных чеков по 2 500 ₽, то есть 28 чеков в день. Сейчас онлайн даёт ноль.")
para(doc, "Цена в часах: пока поток заявок низкий, собственник тратит вечера на рутину и не занимается развитием.")

h(doc, "2. Что внедряем и для кого")
para(doc, "Для частных покупателей в радиусе трёх магазинов: тех, кто ищет «цветы рядом», и тех, кто листает ВК и Telegram.")
for t in [
    "Заполняем карточки трёх магазинов в Google Картах и Яндекс.Бизнесе: фото, часы, услуги, доставка.",
    "Делаем простую витрину: 10–15 букетов с ценами и кнопкой «написать».",
    "Публикуем 3 поста в неделю: букет дня, уход за цветами, повод.",
    "Ставим учёт: откуда пришла заявка — карты, ВК, Telegram, сайт.",
    "Собираем базу клиентов при покупке, чтобы повторные продажи не терялись.",
]:
    para(doc, t, 10, style="List Number")

h(doc, "3. Исходные значения")
table(doc, ["Показатель", "Сейчас", "Источник"], [
    ["Заявки из онлайна", "≈ 0", "со слов, учёта нет"],
    ["Обращения по телефону и в мессенджерах", "0–3 в день", "со слов"],
    ["Подписчики в соцсетях", "3–4 в каждом", "со слов"],
    ["Чеков в день", "20–40", "со слов"],
    ["Средний чек", "2 500 ₽", "со слов"],
    ["Выручка", "2,1 млн ₽ за 28 дней", "со слов"],
    ["Реклама", "5 000 ₽/мес", "со слов"],
], widths=[8.4, 5.0, 3.4])

h(doc, "4. Показатели успеха")
table(doc, ["Показатель", "Цель", "Срок"], [
    ["Заявки из онлайна", "30 за месяц (≈ 1 в день)", "30 дней"],
    ["Подписчики (ВК + Telegram)", "150 суммарно", "60 дней"],
    ["Доля выручки из онлайна", "5% (≈ 105 000 ₽/мес)", "90 дней"],
], widths=[6.8, 6.4, 3.6])
para(doc, "Почему цели скромные: 30 заявок по 2 500 ₽ при конверсии около 70% — это ≈ 50 000 ₽ в месяц. "
          "Для удвоения выручки нужны реклама и 6–12 месяцев, а не месяц. Проект проверяет механику, а не совершает чудо.", 10, italic=True)

h(doc, "5. Первый шаг за 48 часов")
para(doc, "Заполнить карточки трёх магазинов в Google Картах и Яндекс.Бизнесе и опубликовать первый пост «букет дня» с ценой и телефоном. "
          "Всё бесплатно, 2–3 часа.", 10)

h(doc, "Риски и как проверяем")
table(doc, ["Риск", "Что делаем"], [
    ["Заявки есть, но теряются по трём телефонам", "вечерняя сверка: сколько пришло — сколько обработано"],
    ["Подписчики растут, заказов нет", "считаем конверсию из переписки в оплату каждую неделю"],
    ["Витрину забросили", "раз в неделю менять 3 букета и смотреть Метрику"],
    ["Реклама съедает деньги без заявок", "включаем не раньше, чем заработает учёт источников"],
], widths=[7.4, 9.4])

h(doc, "Что не входит в проект")
para(doc, "Мобильное приложение, автоматические рассылки, интеграция с кассой, прогноз закупки по каждой позиции. Это следующий этап, после первых заявок.", 10)

doc.save("proekt.docx")
print("saved proekt.docx")
