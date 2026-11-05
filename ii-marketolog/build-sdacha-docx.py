"""Собирает документ сдачи по домашнему заданию «ИИ-агент маркетолог»."""
from docx import Document
from docx.shared import Pt, Cm, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT

INK = RGBColor(0x3E, 0x40, 0x32)
GREY = RGBColor(0x6E, 0x6C, 0x64)

doc = Document()

# базовый шрифт
style = doc.styles["Normal"]
style.font.name = "Georgia"
style.font.size = Pt(11)
style.paragraph_format.space_after = Pt(6)
style.paragraph_format.line_spacing = 1.15

sec = doc.sections[0]
sec.left_margin = Cm(2.2)
sec.right_margin = Cm(2.2)
sec.top_margin = Cm(2.0)
sec.bottom_margin = Cm(2.0)


def h(text, level=1):
    p = doc.add_heading(text, level=level)
    for r in p.runs:
        r.font.name = "Georgia"
        r.font.color.rgb = INK
        r.font.size = Pt(14 if level == 1 else 12)
        r.font.bold = True
    return p


def para(text, size=11, grey=False, bold=False, after=6):
    p = doc.add_paragraph()
    r = p.add_run(text)
    r.font.size = Pt(size)
    r.font.bold = bold
    r.font.color.rgb = GREY if grey else INK
    p.paragraph_format.space_after = Pt(after)
    return p


def table(headers, rows, widths=None):
    t = doc.add_table(rows=1, cols=len(headers))
    t.style = "Table Grid"
    t.alignment = WD_TABLE_ALIGNMENT.CENTER
    hdr = t.rows[0].cells
    for i, name in enumerate(headers):
        hdr[i].text = ""
        p = hdr[i].paragraphs[0]
        r = p.add_run(name)
        r.font.bold = True
        r.font.size = Pt(10)
        r.font.name = "Georgia"
        r.font.color.rgb = INK
    for row in rows:
        cells = t.add_row().cells
        for i, val in enumerate(row):
            cells[i].text = ""
            p = cells[i].paragraphs[0]
            r = p.add_run(str(val))
            r.font.size = Pt(9.5)
            r.font.name = "Georgia"
            r.font.color.rgb = INK
    if widths:
        for row in t.rows:
            for i, w in enumerate(widths):
                row.cells[i].width = Cm(w)
    doc.add_paragraph().paragraph_format.space_after = Pt(2)
    return t


# ── заголовок
title = doc.add_paragraph()
title.alignment = WD_ALIGN_PARAGRAPH.CENTER
r = title.add_run("ИИ-агент маркетолог «Вова»")
r.font.name = "Georgia"
r.font.size = Pt(24)
r.font.color.rgb = INK
r.font.bold = True

sub = doc.add_paragraph()
sub.alignment = WD_ALIGN_PARAGRAPH.CENTER
r = sub.add_run("Домашнее задание · Silver Song Flowers · 4 ноября 2026")
r.font.size = Pt(10)
r.font.color.rgb = GREY
sub.paragraph_format.space_after = Pt(14)

# ── 1
h("1. Что сделано")
para("Создан работающий ИИ-агент для одной повторяющейся функции бизнеса — маркетинга сети цветочных "
     "магазинов в Санкт-Петербурге. Агент живёт в отдельной папке, знает бизнес, умеет писать посты, "
     "собирать фото под публикацию и планировать продвижение. Запущен в новом сеансе и проверен.")
para("Результат одной строкой: агент готов к ежедневной работе, его задача — заявки из онлайна "
     "(цель 30 заявок за 30 дней при рекламном бюджете 5 000 ₽ в месяц).")

# ── 2
h("2. Функция и критерии приёмки")
table(
    ["Поле", "Содержание"],
    [
        ["Задача", "Онлайн-спрос: тексты, офферы, карточки магазинов, план продвижения"],
        ["Вход", "Файл знаний о бизнесе + задача на конкретный материал"],
        ["Выход", "Готовый материал + список проверок и следующий шаг"],
        ["Критерии приёмки", "Нет выдуманных цифр; всё неподтверждённое помечено «оценка»; "
                             "результат применим без переписывания; указан следующий шаг; "
                             "запреты соблюдены"],
        ["Полномочия", "Сам: черновики, разборы, планы. С согласия: цифры в обещаниях, бюджеты. "
                       "Запрещено: публиковать, менять цены, давать гарантии результата"],
    ],
    widths=[4.2, 12.0],
)

# ── 3
h("3. Из чего состоит агент")
table(
    ["Файл", "Назначение"],
    [
        ["AGENTS.md", "Роль, правила, форматы и стиль. Подхватывается автоматически при открытии папки"],
        ["knowledge.md", "Факты о бизнесе: три точки с адресами и телефонами, цены, экономика, "
                         "сезонность, каналы, цели, палитра бренда"],
        ["skills/", "Восемь инструкций по маркетингу из открытой библиотеки + карта, что когда читать"],
        ["results/", "Готовые материалы: пост с фото, план на 30 дней"],
        ["README.md", "Как включить агента за три шага"],
    ],
    widths=[3.6, 12.6],
)

# ── 4
h("4. Поиск и выбор готовых навыков")
para("Искали на GitHub и в каталоге среды. В среде восемь навыков — все про офисные документы, "
     "для маркетинга не подошли. Выбрана открытая библиотека coreyhaines31/marketingskills (MIT, 53 навыка), "
     "скачаны 8 файлов. Два кандидата отклонены, один остался непроверенным — всё с причинами.")
table(
    ["Кандидат", "Решение"],
    [
        ["coreyhaines31/marketingskills", "Выбран: MIT, 53 навыка с версиями, общий фундамент о продукте и клиенте"],
        ["boraoztunc/skills", "Отклонён: много дизайна, копирайтинг дублирует выбранный"],
        ["floger/antigravity-awesome-skills", "Отклонён: каталог ссылок, каждый навык пришлось бы проверять отдельно"],
        ["alirezarezvani/claude-skills", "Кандидат, не проверен"],
    ],
    widths=[6.0, 10.2],
)

# ── 5
h("5. Испытания")
table(
    ["Испытание", "Что проверяли", "Результат"],
    [
        ["1. Обычная задача", "Пост для ВК на реальных данных", "Выполнено, ожидает приёмки"],
        ["2. Сложная задача", "План на месяц: два канала, бюджет 5 000 ₽", "Выполнено, ожидает приёмки"],
        ["3. Ошибочный вход", "Задача при пустых знаниях о бизнесе", "Пройдено: остановился и задал вопрос, "
                                                                   "ничего не выдумал"],
    ],
    widths=[3.8, 6.4, 6.0],
)

# ── 6
h("6. Настоящие результаты")
para("Пост для группы ВК: фото 1080×1350 и подпись с ценой, тремя адресами и телефонами.")
doc.add_picture("results/foto-post-buket.jpg", width=Cm(9.5))
doc.paragraphs[-1].alignment = WD_ALIGN_PARAGRAPH.CENTER
cap = doc.add_paragraph()
cap.alignment = WD_ALIGN_PARAGRAPH.CENTER
r = cap.add_run("Фото под пост: букет вырезан, фон заменён, бирка с ценой на верёвочке")
r.font.size = Pt(9)
r.font.color.rgb = GREY

para("План на 30 дней: два канала (карточки на картах — бесплатно, ВК — 5 000 ₽), план по неделям, "
     "смета, метрики, риски. Считает цену заявки 167 ₽ при цели 30 заявок и называет это расчётом, "
     "а не обещанием.")

# ── 7
h("7. Ограничения — честно")
para("• Агент не публикует сам: нет доступа к аккаунту ВК и к статистике группы.")
para("• Фотографии обрабатываются из архива, снятого на телефон: вырезка и фон — да, студийная резкость — нет.")
para("• Все цифры экономики — со слов владельца, из кассы не сверены; в знаниях помечены как «оценка».")

# ── 8
h("8. Как запустить")
para("1. Открыть DeepSeek Harness и добавить папку agent-marketolog рабочей областью.")
para("2. Создать в ней новый сеанс.")
para("3. Написать задачу обычными словами: «пост про букет дня», «разбери конкурента на Ленинском».")
para("Инструкция подхватывается автоматически — команду «включись» писать не нужно. Проверено: "
     "агент запущен в новом сеансе и отвечает из файла знаний.")

# ── 9
h("9. Статус")
table(
    ["Компонент", "Состояние"],
    [
        ["Комплект агента", "Собран"],
        ["Навыки", "Подключены как рабочие инструкции"],
        ["Испытания 1–3", "Проведены"],
        ["Повторный запуск в новом сеансе", "Проверен владельцем"],
        ["Приёмка владельцем", "Ожидается"],
    ],
    widths=[8.4, 7.8],
)

para("Вывод: функция проверена в ограниченном режиме — настоящая задача выполнена, испытания пройдены. "
     "Не хватает одного: формальной приёмки результата владельцем.", grey=True)

doc.save("sdacha-ii-marketolog.docx")
print("saved")
