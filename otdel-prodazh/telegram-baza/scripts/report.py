"""Render the classified contact database into a styled XLSX workbook."""
from common import DATA, OUTPUT

import json, io, collections, re
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter
from openpyxl.worksheet.table import Table, TableStyleInfo

DB = str(DATA / "db.json")
OUT = str(OUTPUT / "База_контактов.xlsx")

db = json.load(io.open(DB, encoding="utf-8"))

KIND_RU = {"contractor": "Подрядчик", "expert": "Эксперт", "client": "Клиент / отрасль",
           "institution": "Институция", "personal": "Личное", "service": "Бытовая услуга",
           "junk": "Мусор / SIM", "unknown": "Не определено"}

ASK = {
 "Дизайн / графика": "Портфолио, ставка за макет, сроки, работает ли по договору",
 "Брендинг / айдентика": "Кейсы айдентики, стоимость брендбука, сроки",
 "Копирайт / контент": "Примеры текстов, ставка за 1000 знаков / пакет",
 "SMM / соцсети": "Ведёт ли каналы сам, ставка в месяц, что входит",
 "Performance / таргет": "Бюджеты от какой суммы, кейсы по нише, % или фикс",
 "PR / медиа": "Какие площадки, цена выхода, есть ли личные контакты в редакциях",
 "Видео / монтаж": "Шоурил, смета съёмочного дня, своя техника и монтаж",
 "Фото": "Портфолио, ставка за смену, ретушь включена?",
 "Веб / разработка": "Сроки лендинга, стоимость, поддержка после сдачи",
 "IT / автоматизация / AI": "Какие интеграции делает, кейс бота/CRM, сроки",
 "Юрист / правовое": "Специализация, стоимость консультации и часа",
 "Тендеры / госзакупки": "Опыт 44-ФЗ, готовит ли НМЦК и сметы, цена сопровождения",
 "Бухгалтерия / финансы": "Ведёт ли ООО/ИП, цена в месяц, ответственность",
 "Мероприятия / event": "Что закрывает сам, а что через партнёров; смета",
 "Полиграфия / мерч": "Минимальный тираж, сроки, образцы",
 "Производство": "Что производит, минимальная партия, сроки",
 "Обучение / эксперты": "Тема, формат, гонорар, готова ли запись",
 "Психология": "Специализация, формат, стоимость сессии",
 "HR / найм": "Какие роли закрывает, % от оклада, гарантия",
 "Логистика": "Направления, тариф, сроки",
 "Продажи / B2B": "Может ли подключаться на аутсорс, модель оплаты",
 "Медицина / фарма": "Роль в отрасли, может ли быть экспертом/консультантом",
 "Продюсирование": "Что продюсирует, условия",
 "Бьюти-услуги": "Выезд на съёмку/мероприятие, прайс",
 "Быт-услуги": "Что делает, прайс, сроки",
 "Недвижимость / стройка": "Роль: заказчик, посредник или подрядчик",
 "Медиа / издания": "Тираж/аудитория, цена публикации",
 "Власть / госорганы": "Кто по должности, что решает",
 "Суды / приставы": "По какому делу/участку",
 "Банк": "Кто персональный менеджер, условия для ИП/ООО",
 "Торговля / услуги": "Роль: поставщик или площадка",
 "Телеком": "Сервисный контакт",
 "Личное / семья": "—",
 "Мусор / SIM-сервис": "Удалить из базы",
 "": "Чем занимается — уточнить при следующем контакте",
}

def confidence(p):
    if not p["role"] or p["kind"] in ("junk",): return "низкая"
    if p["cluster"] or p["company"] or p["emails"]: return "высокая"
    if p.get("role_from") == "bio": return "средняя (из профиля)"
    return "средняя"

def link(ws, row, col, url):
    """Turn a cell into a clickable hyperlink (text stays as is)."""
    if not url:
        return
    url = str(url).split(";")[0].strip()
    if not url:
        return
    if not url.lower().startswith("http"):
        url = "https://" + url
    c = ws.cell(row=row, column=col)
    if not c.value:
        c.value = re.sub(r"^https?://", "", url)
    elif str(c.value).lower().startswith("http"):
        c.value = re.sub(r"^https?://", "", str(c.value)).rstrip("/")
    c.hyperlink = url
    c.font = Font(size=9, color="0563C1", underline="single")

def phone_str(p, i=0):
    if len(p["phones"]) > i: return p["phones"][i]["num"]
    return ""

HDR_FILL = PatternFill("solid", fgColor="1F3864")
HDR_FONT = Font(color="FFFFFF", bold=True, size=10)
SEG_FILL = {"A": PatternFill("solid", fgColor="C6EFCE"), "B": PatternFill("solid", fgColor="FFEB9C"),
            "C": PatternFill("solid", fgColor="F2F2F2"), "—": PatternFill("solid", fgColor="FFFFFF")}
THIN = Side(style="thin", color="D9D9D9")
BORDER = Border(left=THIN, right=THIN, top=THIN, bottom=THIN)

def style_header(ws, ncols, row=1):
    for c in range(1, ncols + 1):
        cell = ws.cell(row=row, column=c)
        cell.fill = HDR_FILL; cell.font = HDR_FONT
        cell.alignment = Alignment(vertical="center", horizontal="center", wrap_text=True)
    ws.row_dimensions[row].height = 30

def autosize(ws, widths):
    for i, w in enumerate(widths, start=1):
        ws.column_dimensions[get_column_letter(i)].width = w

wb = Workbook()

# ------------------------------------------------------------------ Сводка
ws = wb.active; ws.title = "Сводка"
n = len(db)
n_company = sum(1 for p in db if p["company"])
n_email = sum(1 for p in db if p["emails"])
n_phone = sum(1 for p in db if p["phones"])
kinds = collections.Counter(p["kind"] for p in db)
segs = collections.Counter(p["segment"] for p in db)
workers = [p for p in db if p["kind"] in ("contractor", "expert", "service")]
ab = [p for p in workers if p["segment"] in ("A", "B")]

ws["A1"] = "База контактов A51 → подрядчики для проектов"
ws["A1"].font = Font(bold=True, size=16, color="1F3864")
ws["A2"] = f"Телефон Samsung SM-A515F (ADB) + Telegram (2 аккаунта) · {n} контактов после дедупликации"
ws["A2"].font = Font(size=10, italic=True, color="595959")

rows = [
 ("Всего контактов в базе", n, "после объединения дублей из Google, Samsung, WhatsApp, Telegram"),
 ("  · в т.ч. только из Telegram", sum(1 for p in db if p["source"] == "Telegram"), "контакты, которых не было в телефонной книге"),
 ("  · в т.ч. совпали", sum(1 for p in db if p["source"] == "Телефон + Telegram"), "были и в телефоне, и в Telegram — склеены"),
 ("  · найдены в чате «Кузница Брендов_Управление»", sum(1 for p in db if p.get("tg_chat")), "упомянуты в рабочем чате, добавлены с профилями и ссылками"),
 ("Подрядчиков и экспертов", len(workers), "те, кого в принципе можно нанять на работу"),
 ("  · сегмент A — готовы к проекту", segs.get("A", 0), "ясная роль + подтверждённая связь"),
 ("  · сегмент B — потенциал", segs.get("B", 0), "роль ясна, но опыт не подтверждён"),
 ("  · сегмент C — слабый сигнал", segs.get("C", 0), "роль угадывается по имени"),
 ("Клиенты и отраслевые контакты", kinds.get("client", 0), "заказчики, фарма-поле, издания"),
 ("Институции и сервисы", kinds.get("institution", 0), "банки, клиники, МФЦ, телеком"),
 ("Личные контакты", kinds.get("personal", 0), "семья, друзья, соседи"),
 ("Не определено", kinds.get("unknown", 0), "только имя — роль нужно уточнять"),
 ("SIM-мусор", kinds.get("junk", 0), "служебные записи оператора, удалить"),
]
r = 4
ws.cell(row=r, column=1, value="Показатель").font = Font(bold=True, color="FFFFFF")
ws.cell(row=r, column=1).fill = HDR_FILL
ws.cell(row=r, column=2, value="Значение").font = Font(bold=True, color="FFFFFF")
ws.cell(row=r, column=2).fill = HDR_FILL
ws.cell(row=r, column=3, value="Комментарий").font = Font(bold=True, color="FFFFFF")
ws.cell(row=r, column=3).fill = HDR_FILL
for i, (a, b, c) in enumerate(rows, start=r + 1):
    ws.cell(row=i, column=1, value=a).font = Font(bold=(i == r + 1))
    ws.cell(row=i, column=2, value=b).alignment = Alignment(horizontal="center")
    ws.cell(row=i, column=3, value=c).font = Font(size=9, color="595959")

r2 = r + len(rows) + 3
ws.cell(row=r2, column=1, value="Что внутри").font = Font(bold=True, size=12, color="1F3864")
guide = [
 ("Подрядчики", "Сегменты A и B: готовый шорт-лист с телефонами и вопросом для первого звонка"),
 ("Задачи", "Матрица «задача проекта → кто может закрыть» — 5 кандидатов на каждую"),
 ("Пробелы", "Где в базе нет исполнителей: эти роли надо искать на стороне"),
 ("Роли", "Сколько подрядчиков по каждому направлению и как они распределены"),
 ("База", "Полная выгрузка со всеми признаками — фильтруйте по любому столбцу"),
 ("Методика", "Как считались признаки и скор — чтобы можно было оспорить или поправить"),
]
for i, (a, b) in enumerate(guide, start=r2 + 1):
    ws.cell(row=i, column=1, value=a).font = Font(bold=True)
    ws.cell(row=i, column=3, value=b).font = Font(size=9, color="404040")
    ws.merge_cells(start_row=i, start_column=3, end_row=i, end_column=6)

autosize(ws, [38, 12, 62, 14, 14, 14])

# ------------------------------------------------------------------ Подрядчики
ws = wb.create_sheet("Подрядчики")
cols = ["Сегмент", "Скор", "Роль", "Имя в телефоне", "Телефон", "Доп. телефон", "E-mail",
        "Компания", "Кластер", "Telegram", "Канал", "Чат", "Сайт", "Портфолио", "От кого", "Уверенность", "Что уточнить"]
ws.append(cols)
for p in ab:
    ws.append([p["segment"], p["score"], p["role"], p["name"], phone_str(p, 0), phone_str(p, 1),
               p["emails"][0]["email"] if p["emails"] else "", p["company"], p["cluster"],
               p.get("tg_username", ""), p.get("tg_channel", ""), p.get("tg_chat", ""),
               p.get("site", ""), p.get("portfolio", ""),
               p["referral"], confidence(p), ASK.get(p["role"], ASK[""])])
style_header(ws, len(cols))
for i, p in enumerate(ab, start=2):
    ws.cell(row=i, column=1).fill = SEG_FILL[p["segment"]]
    ws.cell(row=i, column=1).alignment = Alignment(horizontal="center")
    ws.cell(row=i, column=2).alignment = Alignment(horizontal="center")
    for c in range(1, len(cols) + 1):
        ws.cell(row=i, column=c).border = BORDER
        ws.cell(row=i, column=c).font = Font(size=10)
    link(ws, i, 10, p.get("tg_url") or (f"https://t.me/{p['tg_username'].split('; ')[0]}" if p.get("tg_username") else ""))
    link(ws, i, 11, p.get("tg_channel"))
    link(ws, i, 13, p.get("site"))
    link(ws, i, 14, p.get("portfolio"))
ws.freeze_panes = "D2"
ws.auto_filter.ref = f"A1:{get_column_letter(len(cols))}{len(ab)+1}"
autosize(ws, [9, 7, 24, 44, 18, 18, 26, 22, 16, 24, 28, 22, 30, 30, 12, 12, 48])

# ------------------------------------------------------------------ База
ws = wb.create_sheet("База")
cols = ["№", "Сегмент", "Скор", "Роль", "Тип", "Источник", "Имя в телефоне", "Телефон", "Доп. телефон",
        "E-mail", "Компания", "Кластер", "Telegram", "Канал", "Чат", "Сайт", "Портфолио", "Соцсети", "О себе",
        "Город", "От кого", "Все роли", "Группы", "Уверенность", "Что уточнить"]
ws.append(cols)
for idx, p in enumerate(db, start=1):
    ws.append([idx, p["segment"], p["score"], p["role"], KIND_RU.get(p["kind"], p["kind"]),
               p["source"], p["name"], phone_str(p, 0), phone_str(p, 1),
               p["emails"][0]["email"] if p["emails"] else "", p["company"], p["cluster"],
               p.get("tg_username", ""), p.get("tg_channel", ""), p.get("tg_chat", ""),
               p.get("site", ""), p.get("portfolio", ""),
               p.get("socials", ""), p.get("bio", ""),
               p["city"], p["referral"], "; ".join(p["roles_all"]), ", ".join(p["groups"]),
               confidence(p), ASK.get(p["role"], ASK[""])])
style_header(ws, len(cols))
for i, p in enumerate(db, start=2):
    ws.cell(row=i, column=2).fill = SEG_FILL[p["segment"]]
    ws.cell(row=i, column=2).alignment = Alignment(horizontal="center")
    ws.cell(row=i, column=3).alignment = Alignment(horizontal="center")
    for c in range(1, len(cols) + 1):
        ws.cell(row=i, column=c).font = Font(size=9)
    link(ws, i, 13, p.get("tg_url") or (f"https://t.me/{p['tg_username'].split('; ')[0]}" if p.get("tg_username") else ""))
    link(ws, i, 14, p.get("tg_channel"))
    link(ws, i, 16, p.get("site"))
    link(ws, i, 17, p.get("portfolio"))
ws.freeze_panes = "C2"
ws.auto_filter.ref = f"A1:{get_column_letter(len(cols))}{len(db)+1}"
autosize(ws, [6, 9, 7, 24, 16, 18, 44, 18, 18, 26, 22, 16, 24, 28, 22, 30, 30, 36, 50, 12, 11, 34, 20, 12, 44])

# ------------------------------------------------------------------ Задачи
TASKS = [
 ("Брендинг и айдентика", ["Брендинг / айдентика", "Дизайн / графика"]),
 ("Дизайн: полиграфика, презентации", ["Дизайн / графика"]),
 ("Сайт / лендинг", ["Веб / разработка"]),
 ("Реклама: таргет и SMM", ["Performance / таргет", "SMM / соцсети"]),
 ("Контент и копирайт", ["Копирайт / контент"]),
 ("Видео и фотосъёмка", ["Видео / монтаж", "Фото"]),
 ("PR и публикации", ["PR / медиа", "Медиа / издания"]),
 ("Мероприятие под ключ", ["Мероприятия / event"]),
 ("Полиграфия и мерч", ["Полиграфия / мерч", "Производство"]),
 ("Тендер / НМЦК / 44-ФЗ", ["Тендеры / госзакупки"]),
 ("Юридическое сопровождение", ["Юрист / правовое"]),
 ("Бухгалтерия и налоги", ["Бухгалтерия / финансы"]),
 ("Найм и HR", ["HR / найм"]),
 ("Обучение и спикеры", ["Обучение / эксперты", "Психология"]),
 ("Медицина и фарма (отрасль)", ["Медицина / фарма"]),
 ("Автоматизация и AI-боты", ["IT / автоматизация / AI"]),
]
ws = wb.create_sheet("Задачи")
cols = ["Задача проекта", "Кто нужен", "Доступно A/B", "Кандидат 1", "Кандидат 2", "Кандидат 3", "Кандидат 4", "Кандидат 5"]
ws.append(cols)
gap_rows = []
for task, roles in TASKS:
    cands = [p for p in workers if p["segment"] in ("A", "B") and (p["role"] in roles or any(r in roles for r in p["roles_all"]))]
    cands.sort(key=lambda x: (-x["score"], x["name"]))
    a_count = sum(1 for p in cands if p["segment"] == "A")
    row = [task, " / ".join(roles), f"{a_count} / {len(cands) - a_count}"]
    for c in cands[:5]:
        tag = " (A)" if c["segment"] == "A" else ""
        row.append(f'{c["name"]}{tag} — {phone_str(c,0)}')
    ws.append(row)
    gap_rows.append((task, a_count, len(cands)))
style_header(ws, len(cols))
for i in range(2, len(TASKS) + 2):
    for c in range(1, len(cols) + 1):
        ws.cell(row=i, column=c).border = BORDER
        ws.cell(row=i, column=c).alignment = Alignment(vertical="top", wrap_text=(c > 3))
        ws.cell(row=i, column=c).font = Font(size=10)
    ws.row_dimensions[i].height = 42
autosize(ws, [30, 26, 12, 34, 34, 34, 34, 34])

# ------------------------------------------------------------------ Пробелы
ws = wb.create_sheet("Пробелы")
cols = ["Задача", "Сегмент A", "Сегмент B", "Всего", "Вывод", "Что делать"]
ws.append(cols)
for task, a_count, total in gap_rows:
    if a_count >= 2:
        verdict, action = "закрыто", "есть выбор — можно сравнивать условия"
    elif a_count == 1:
        verdict, action = "узкое место", "один исполнитель — найти дублёра"
    elif total > 0:
        verdict, action = "риск", "только непроверенные — проверить портфолио"
    else:
        verdict, action = "пробел", "исполнителя в базе нет — искать отдельно"
    ws.append([task, a_count, total - a_count, total, verdict, action])
style_header(ws, len(cols))
for i in range(2, len(gap_rows) + 2):
    for c in range(1, len(cols) + 1):
        ws.cell(row=i, column=c).border = BORDER
        ws.cell(row=i, column=c).font = Font(size=10, bold=(c == 5))
autosize(ws, [32, 11, 11, 8, 16, 46])

# ------------------------------------------------------------------ Роли
ws = wb.create_sheet("Роли")
cols = ["Роль", "A", "B", "C", "Всего", "Всего контактов с этой ролью", "Комментарий"]
ws.append(cols)
role_stats = []
for role in sorted({p["role"] for p in workers if p["role"]}):
    a = sum(1 for p in workers if p["role"] == role and p["segment"] == "A")
    b = sum(1 for p in workers if p["role"] == role and p["segment"] == "B")
    c = sum(1 for p in workers if p["role"] == role and p["segment"] == "C")
    allr = sum(1 for p in db if p["role"] == role)
    role_stats.append((role, a, b, c, allr))
role_stats.sort(key=lambda x: (-(x[1] + x[2]), -x[4]))
for role, a, b, c, allr in role_stats:
    note = "сильная роль" if a + b >= 8 else ("рабочая" if a + b >= 3 else "мало исполнителей")
    ws.append([role, a, b, c, a + b + c, allr, note])
style_header(ws, len(cols))
for i in range(2, len(role_stats) + 2):
    for c in range(1, len(cols) + 1):
        ws.cell(row=i, column=c).border = BORDER
        ws.cell(row=i, column=c).font = Font(size=10)
autosize(ws, [30, 7, 7, 7, 8, 24, 26])

# ------------------------------------------------------------------ Из чата
ws = wb.create_sheet("Из чата")
chat_people = sorted([p for p in db if p.get("tg_chat")], key=lambda x: (-x["score"], x["name"]))
cols = ["Сегмент", "Скор", "Роль", "Имя", "Telegram", "Телефон", "Канал", "Сайт", "Портфолио", "О себе", "Контекст в чате"]
ws["A1"] = (", ".join(sorted({p["tg_chat"] for p in chat_people})) or "Рабочий чат") + " — люди и сервисы, упомянутые в чате"
ws["A1"].font = Font(size=13, bold=True, color="1F3864")
ws["A2"] = f"{len(chat_people)} карточек · {sum(1 for p in chat_people if p['kind'] in ('contractor','expert'))} подрядчиков и экспертов · контекст взят из сообщения, где человек упомянут"
ws["A2"].font = Font(size=9, italic=True, color="595959")
hdr_row = 4
for j, c in enumerate(cols, start=1):
    ws.cell(row=hdr_row, column=j, value=c)
style_header(ws, len(cols), row=hdr_row)
for i, p in enumerate(chat_people, start=hdr_row + 1):
    ws.cell(row=i, column=1, value=p["segment"]).fill = SEG_FILL[p["segment"]]
    ws.cell(row=i, column=1).alignment = Alignment(horizontal="center")
    ws.cell(row=i, column=2, value=p["score"]).alignment = Alignment(horizontal="center")
    ws.cell(row=i, column=3, value=p["role"])
    ws.cell(row=i, column=4, value=p["name"])
    ws.cell(row=i, column=5, value=p.get("tg_username", ""))
    ws.cell(row=i, column=6, value=phone_str(p, 0))
    ws.cell(row=i, column=7, value=p.get("tg_channel", ""))
    ws.cell(row=i, column=8, value=p.get("site", ""))
    ws.cell(row=i, column=9, value=p.get("portfolio", ""))
    ws.cell(row=i, column=10, value=p.get("bio", ""))
    ws.cell(row=i, column=11, value=p.get("note") or "")
    for c in range(1, len(cols) + 1):
        ws.cell(row=i, column=c).border = BORDER
        ws.cell(row=i, column=c).font = Font(size=9)
    link(ws, i, 5, p.get("tg_url") or (f"https://t.me/{p['tg_username'].split('; ')[0]}" if p.get("tg_username") else ""))
    link(ws, i, 7, p.get("tg_channel"))
    link(ws, i, 8, p.get("site"))
    link(ws, i, 9, p.get("portfolio"))
ws.freeze_panes = f"D{hdr_row + 1}"
ws.auto_filter.ref = f"A{hdr_row}:{get_column_letter(len(cols))}{hdr_row + len(chat_people)}"
autosize(ws, [9, 7, 24, 34, 22, 18, 28, 26, 26, 44, 56])

# ------------------------------------------------------------------ Методика
ws = wb.create_sheet("Методика")
lines = [
 ("Как построена база", "h1"),
 ("1. Источник", "h2"),
 ("Контакты выгружены напрямую с телефона Samsung SM-A515F через ADB (content provider "
  "com.android.contacts): таблицы raw_contacts, data, contacts, groups. Это полная база, "
  "включая Google-аккаунты, Samsung, WhatsApp Business и SIM.", "p"),
 (f"Telegram добавлен напрямую через Telethon: две авторизованные сессии — личный аккаунт "
  f"(@asemchuk) и «Кому.маркетинг» (@Komumarketing). Всего {sum(1 for p in db if 'Telegram' in p['source'])} карточек "
  f"связаны с Telegram, из них {sum(1 for p in db if p['source'] == 'Telegram')} — люди, которых в телефонной "
  f"книге не было вовсе. Совпадения искались по номеру телефона, поэтому дублей между источниками нет.", "p"),
 (f"Ссылки взяты из профилей: {sum(1 for p in db if p.get('tg_channel'))} карточек с личным каналом, "
  f"{sum(1 for p in db if p.get('site'))} с сайтом, {sum(1 for p in db if p.get('portfolio'))} с портфолио, "
  f"{sum(1 for p in db if p.get('bio'))} с текстом «о себе». Сайт, канал и портфолио вытащены из описания профиля "
  f"автоматически, поэтому иногда там ссылка на соцсеть или на чужой ресурс — это стоит проверять глазами. "
  f"Если в имени роли не было, она определялась по описанию профиля; такие строки помечены «средняя (из профиля)».", "p"),
 (f"Отдельно разобран рабочий чат «Кузница Брендов_Управление»: прочитано 1 598 сообщений, собраны все упоминания "
  f"@username и ссылки t.me, каждое раскрыто в профиль. Боты отброшены, нераскрытые упоминания оставлены ссылкой "
  f"на профиль. Такие карточки помечены в колонке «Чат», а контекст — фраза, в которой человек упомянут, — вынесен "
  f"на лист «Из чата».", "p"),
 ("2. Дедупликация", "h2"),
 ("Android уже склеивает один и тот же контакт из разных аккаунтов, но остаются ручные дубли. "
  "Склейка шла по совпадению номера телефона с проверкой совместимости имён, поэтому разные люди "
  "с общим рабочим номером не схлопнулись в одного.", "p"),
 ("3. Признаки, по которым раскладывал", "h2"),
 ("Роль / профессия — что человек умеет делать руками или головой (дизайн, видео, юрист, бухгалтер). "
  "Это главный признак полезности как подрядчика.", "p"),
 ("Тип контрагента — подрядчик (можно нанять), эксперт (носитель компетенции: тренер, врач, психолог), "
  "клиент/отрасль (фарма-поле, издания, застройщики), институция (банк, клиника, МФЦ), личное (семья, друзья).", "p"),
 ("Кластер — принадлежность к вашему проекту или сети: Cissa, Терра, МБК, Грифон, ЖК ЗК, "
  "фарма/медиа-сеть. Контакты из своих проектов ценнее: вы уже знаете, как они работают.", "p"),
 ("Уверенность — высокая, если роль подтверждена кластером, компанией или e-mail; средняя, если роль "
  "видна только из подписи в имени; низкая, если это просто имя без признаков.", "p"),
 ("4. Скор 0–100", "h2"),
 ("Скор = 55% вес роли + 25% принадлежность к вашей сети + 20% полнота данных. "
  "Вес роли отражает, насколько часто такая компетенция нужна в ваших проектах: таргет, разработка, "
  "видео, дизайн, тендеры — 10; event, юристы, бухгалтерия — 8–9; обучение и эксперты — 7; "
  "банки и телеком — 1–2.", "p"),
 ("A — 65 и выше: роль ясна и есть подтверждение. B — 45–64: роль ясна, опыт нет. "
  "C — ниже 45: слабый сигнал, нужен разговор.", "p"),
 ("5. Ограничение, которое важно понимать", "h2"),
 (f"В телефонной книге почти нет должностей и компаний: только {n_company} контактов с организацией "
  f"и {n_email} с e-mail. "
  "Поэтому роль восстановлена по словам в имени («Дизайнер», «Бухгалтер», «Ведущий») и по кластерам. "
  "Там, где имени недостаточно, стоит «Не определено» — это честнее, чем угадывать. "
  "База доводится до рабочего состояния не выгрузкой, а десятью звонками: в листе «Подрядчики» "
  "у каждого стоит вопрос, который закрывает пробел.", "p"),
 ("6. Что делать дальше", "h2"),
 ("Пройти по сегменту A (33 контакта) и зафиксировать: специализация, ставка, сроки, готовность "
  "работать по договору и с НДС. Это превращает список имён в управляемую базу подрядчиков. "
  "Затем закрыть пробелы из одноимённого листа — там видно, каких ролей в базе физически нет.", "p"),
]
r = 1
for text, kind in lines:
    c = ws.cell(row=r, column=1, value=text)
    if kind == "h1":
        c.font = Font(bold=True, size=15, color="1F3864"); r += 2
    elif kind == "h2":
        c.font = Font(bold=True, size=11, color="1F3864"); r += 1
    else:
        c.font = Font(size=10); c.alignment = Alignment(wrap_text=True, vertical="top")
        ws.merge_cells(start_row=r, start_column=1, end_row=r, end_column=6)
        ws.row_dimensions[r].height = max(30, 15 * (len(text) // 95 + 1))
        r += 1
ws.column_dimensions["A"].width = 118

wb.save(OUT)
print("saved", OUT)
print("sheets:", wb.sheetnames)
print("rows: база", len(db), "| подрядчики", len(ab))
