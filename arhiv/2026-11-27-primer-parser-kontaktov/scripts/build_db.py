"""v2: dedupe + classify contacts into a contractor database."""
from common import DATA, OUTPUT

import json, re, io, collections, unicodedata, os

SRC = str(DATA / "people_all.json")
if not os.path.exists(SRC):
    SRC = str(DATA / "people.json")
OUT = str(DATA / "db.json")

# role, regex, weight (value as contractor for her projects 0-10), kind
RULES = [
 ("Performance / таргет",     r"таргет|яндекс ?директ|директолог|\bдирект\b|performance|трафик|лидоген|медиаплан", 10, "contractor"),
 ("Веб / разработка",         r"сайт|веб-|вебсайт|\bвеб\b|\bweb\b|web-|лендинг|тильда|tilda|разработ|программист|программер|frontend|backend", 10, "contractor"),
 ("IT / автоматизация / AI",  r"\bit\b|айти|бот|телеграм|crm|битрикс|amocrm|автоматизац|нейросет|gpt|\bai\b|\b1с\b|датамайн", 10, "contractor"),
 ("Видео / монтаж",           r"видео|видеограф|монтаж|оператор|съемк|съёмк|сторис|ролик|ютуб|youtube|студия записи", 10, "contractor"),
 ("Дизайн / графика",         r"дизайн|верстк|верстальщ|figma|иллюстрат|арт-директор", 10, "contractor"),
 ("Тендеры / госзакупки",     r"тендер|закупк|нмцк|\bсмет|44-фз|госзаказ", 10, "contractor"),
 ("Брендинг / айдентика",     r"брендинг|бренд-|айдентик|логотип", 9, "contractor"),
 ("Копирайт / контент",       r"копирайт|контент|редактор|сценарист|райтер", 9, "contractor"),
 ("SMM / соцсети",            r"\bсмм\b|\bsmm\b|соцсет|инстаграм|instagram|\binst\b|контент-план", 9, "contractor"),
 ("PR / медиа",               r"пиар|pr[- ]|pr$|пресс-служ|медиаменеджер|спикерство|pr tv", 9, "contractor"),
 ("Юрист / правовое",         r"юрист|адвокат|нотариус|арбитраж|роскомнадзор|\bркн\b|патент|правов", 9, "contractor"),
 ("Мероприятия / event",      r"ведущ|шоумен|тамада|мероприят|площадк|кейтеринг|звук|свет|диджей|\bdj\b|организатор|конгресс|конгресс-центр", 9, "contractor"),
 ("Бухгалтерия / финансы",    r"бухгалт|\bбух\b|налог|аудит|финанс|экономист", 8, "contractor"),
 ("Полиграфия / мерч",        r"полиграф|типограф|печат|листовк|мерч|сувенир|баннер|наружн", 8, "contractor"),
 ("Фото",                     r"фотограф|фотосесс|\bфото\b", 8, "contractor"),
 ("HR / найм",                r"\bhr\b|кадров|кадры|\bкадр\b|рекрут|персонал|найм|подбор|hrservices", 8, "contractor"),
 ("Обучение / эксперты",      r"бизнес-тренер|тренер|коуч|наставник|эксперт|спикер|преподават|репетитор|школ|обучен|курс|университет|институт|акселератор", 7, "expert"),
 ("Продюсирование",           r"продюссер|продюсер", 7, "contractor"),
 ("Логистика",                r"логист|доставк|курьер|транспорт|перевозк|контейнер|грузоперевоз", 6, "contractor"),
 ("Продажи / B2B",            r"продаж|\bb2b\b|коммерческ|кол-центр|колцентр|холодные звонки", 6, "contractor"),
 ("Психология",               r"психолог|психотерап|психиатр|нумеролог", 6, "expert"),
 ("Производство",             r"производств|завод|фабрик|стекло|поставк", 6, "contractor"),
 ("Медицина / фарма",         r"клиник|поликлиник|стоматолог|врач|хирург|медсестр|мед\.|аптек|косметолог|фарм|главврач|медпред|медфорум|медицинск|медвестник|лор\b|педиатр|рм\b", 5, "expert"),
 ("Бьюти-услуги",             r"визажист|барбер|маникюр|парикмахер|бровист|ресниц", 4, "service"),
 ("Быт-услуги",               r"клининг|электрик|сантехник|грузчик|мебель|шторы|натяжн|окна|двери|мастер по", 3, "service"),
 ("Недвижимость / стройка",   r"\bжк\b|жк ?зк|строй|ремонт|недвижим|риелтор|застройщик|квартир|парковк|аренд", 5, "client"),
 ("Власть / госорганы",       r"администрац|комитет|департамент|министерств|\bмфц\b|управа|госуслуг|фнс|рспп|росмолодеж", 3, "institution"),
 ("Суды / приставы",          r"пристав|судебн|канцелярия|алимент", 3, "institution"),
 ("Банк",                     r"банк|сбер|тинькоф|альфа|втб|ситибанк|рассрочк|кредит", 2, "institution"),
 ("Медиа / издания",          r"медиа|журнал|газет|издател|редакц|\bпресс\b|вестник", 5, "client"),
 ("Торговля / услуги",        r"магазин|салон|ателье|кафе|ресторан|отель|копицентр|одежда", 2, "institution"),
 ("Телеком",                  r"\bмтс\b|билайн|мегафон|tele2|теле2|модем", 1, "institution"),
]

# field-force / corporate prefixes she uses in her own address book
FF = re.compile(r"^(рм|мп|ол|кол|вм|дд|мсд)\s", re.I)

PERSONAL = r"мама|папа|бабушк|дедушк|\bбрат\b|сестр|сын\b|дочь|дочк|жена|\bмуж\b|сосед|кум|т[её]тя|дядя|семья|подруг|сваха|крестн|племянник|племянниц"
JUNK = re.compile(r"^\d{2}[\s.]|generated|отзывы|копия контактов|служба спасения|мой номер|баланс|sms|архив|погода|гороскоп|знакомств|^книги|пресса|скидки|развлечен|курс валют|good'?ok|мтс music|мтс сервис|услуги мтс|^контур$|^невалинк$|^hays$", re.I)

CLUSTERS = [
 # Свои рабочие группы и компании: ("Название", r"регex по имени или компании").
 # Пустой список — нормально, тогда кластеры просто не определяются.
 # Пример: ("Моя школа",   r"моя ?школа"),
 #         ("Агентство X",  r"агентство ?х|agentstvo ?x"),
]

def norm(s):
    s = unicodedata.normalize("NFKC", s or "").lower()
    s = re.sub(r"[\u2700-\u27bf\U0001F000-\U0001FAFF]", " ", s)
    s = re.sub(r"[^а-яёa-z0-9@.\s-]", " ", s)
    return re.sub(r"\s+", " ", s).strip()

def digits(s):
    d = re.sub(r"\D", "", s or "")
    if len(d) == 11 and d[0] in "78":
        d = d[1:]
    return d if len(d) >= 10 else ""

STOP = set("от и в на по для с у не".split())
CITY = set("спб питер москва москве томск тверь норильск дудинка сертолово чебоксары екатеринбург новгород нижний калининград воронеж иркутск казань".split())

def toks(n):
    return {t for t in n.split() if len(t) > 2 and t not in STOP and t not in CITY}

ORG_LIKE = re.compile(r"(ооо|оао|зао|пао|ано|\bип\b|банк|клиник|поликлиник|школ|салон|аптек|магазин|центр|агентств|студи|компани|групп|сервис|мтс|билайн|мегафон|\bжк\b|отель|кафе|ресторан|фонд|комитет|администрац|департамент|министерств|мфц|сбер|тинькоф|альфа|втб|телеком)")

def is_person_like(n):
    if not n or re.search(r"\d", n): return False
    if ORG_LIKE.search(n): return False
    return 1 <= len(n.split()) <= 4

class UF:
    def __init__(self): self.p = {}
    def find(self, x):
        self.p.setdefault(x, x)
        while self.p[x] != x:
            self.p[x] = self.p[self.p[x]]; x = self.p[x]
        return x
    def union(self, a, b):
        ra, rb = self.find(a), self.find(b)
        if ra != rb: self.p[rb] = ra

def build():
    people = json.load(io.open(SRC, encoding="utf-8"))

    uf, by_phone = UF(), collections.defaultdict(list)
    for i, p in enumerate(people):
        uf.find(i)
        for ph in p["phones"]:
            d = digits(ph["num"])
            if d: by_phone[d].append(i)
    for d, idxs in by_phone.items():
        uniq = sorted(set(idxs))
        for a in uniq:
            for b in uniq:
                if a >= b: continue
                na, nb = norm(people[a]["name"]), norm(people[b]["name"])
                if not (na and nb):
                    continue
                if na in nb or nb in na or (toks(na) & toks(nb)):
                    uf.union(a, b)
                elif is_person_like(na) and is_person_like(nb):
                    # same mobile in two sources -> same human even if the name differs
                    uf.union(a, b)

    groups = collections.defaultdict(list)
    for i in range(len(people)):
        groups[uf.find(i)].append(people[i])

    merged = []
    for members in groups.values():
        extra = {}
        for m in members:
            for k in ("tg_url", "tg_channel", "tg_chat", "site", "portfolio", "socials", "bio"):
                if not extra.get(k) and m.get(k):
                    extra[k] = m[k]
        groups_, accounts, handles = set(), set(), set()
        phones, emails, comps, notes = [], [], [], []
        starred, names = 0, []
        seen_ph = set()
        for m in members:
            if m["name"]: names.append(m["name"].strip())
            for h in (m.get("tg_username") or "").split(";"):
                if h.strip(): handles.add(h.strip())
            for ph in m["phones"]:
                key = digits(ph["num"]) or ph["num"]
                if key in seen_ph: continue
                seen_ph.add(key); phones.append(ph)
            for em in m["emails"]:
                if em["email"] not in [x["email"] for x in emails]: emails.append(em)
            if m["company"]: comps.append(m["company"])
            if m["note"]: notes.append(m["note"])
            groups_ |= set(m["groups"]); accounts |= set(m["accounts"])
            starred = max(starred, m["starred"] or 0)
        names.sort(key=len, reverse=True)
        name = names[0] if names else ""
        name = re.sub(r"^\+?\d[\d\s()\-]{9,}\s*", "", name).strip() or name
        merged.append({
            "name": name, "alt_names": names[1:4], "phones": phones[:4],
            "emails": emails[:2], "company": next((c for c in comps if c), ""),
            "note": " | ".join(dict.fromkeys(notes))[:300],
            "groups": sorted(groups_), "accounts": sorted(accounts),
            "starred": starred, "n_sources": len(members),
            "tg_username": "; ".join(sorted(handles)),
            **extra,
        })

    for p in merged:
        n = norm(p["name"])
        accs = set(p["accounts"])
        has_tg = "com.telegram.messenger" in accs
        p["source"] = ("Телефон + Telegram" if has_tg and (accs - {"com.telegram.messenger"})
                       else ("Telegram" if has_tg else "Телефон"))
        p["junk"] = bool(JUNK.search(p["name"]))
        p["is_personal"] = bool(re.search(PERSONAL, n))
        matched = [(r, w, k) for r, rx, w, k in RULES if re.search(rx, n)]
        p["role_from"] = "name" if matched else ""
        if not matched and p.get("bio"):
            nb = norm(p["bio"])
            matched = [(r, w, k) for r, rx, w, k in RULES if re.search(rx, nb)]
            if matched:
                p["role_from"] = "bio"
        matched.sort(key=lambda x: -x[1])
        p["roles_all"] = [m[0] for m in matched]
        p["role"] = matched[0][0] if matched else ""
        p["role_weight"] = matched[0][1] if matched else 0
        p["kind"] = matched[0][2] if matched else "unknown"
        p["ff"] = bool(FF.match(p["name"]))

        if p["junk"]:
            p["kind"], p["role"], p["role_weight"] = "junk", "Мусор / SIM-сервис", 0
        elif p["is_personal"]:
            p["kind"], p["role"], p["role_weight"] = "personal", "Личное / семья", 0

        p["cluster"] = next((c for c, rx in CLUSTERS if re.search(rx, n)), "")
        mref = re.search(r"\bот\s+([А-ЯЁ][а-яё]+)", p["name"])
        p["referral"] = mref.group(1) if mref else ""
        mc = re.search(r"\b(СПб|Питер|Москва|Томск|Тверь|Норильск|Дудинка|Сертолово|Чебоксары|Екатеринбург|Новгород|Калининград|Воронеж|Иркутск|Казань)\b", p["name"], re.I)
        p["city"] = mc.group(1) if mc else ""

        ev = (1 if p["company"] else 0) + (1 if p["emails"] else 0) + (1 if p["starred"] else 0) + (1 if len(p["phones"]) > 1 else 0)
        net = 1 if (p["cluster"] or p["company"]) else 0
        w = p["role_weight"]
        score = 0.55 * (w / 10 * 100) + 0.25 * net * 100 + 0.20 * (ev / 4 * 100)
        p["evidence"], p["score"] = ev, round(score)

    merged.sort(key=lambda x: (-x["score"], x["name"]))
    for p in merged:
        if p["kind"] in ("contractor", "expert", "service"):
            p["segment"] = "A" if p["score"] >= 65 else ("B" if p["score"] >= 45 else "C")
        else:
            p["segment"] = "—"

    json.dump(merged, io.open(OUT, "w", encoding="utf-8"), ensure_ascii=False, indent=1)

    print(f"contacts: {len(merged)}")
    print("kinds:", collections.Counter(p["kind"] for p in merged).most_common())
    print("segments:", collections.Counter(p["segment"] for p in merged).most_common())
    print("roles:")
    for r, c in collections.Counter(p["role"] for p in merged if p["role"]).most_common():
        print(f"   {c:4d}  {r}")
    print("clusters:", collections.Counter(p["cluster"] for p in merged if p["cluster"]).most_common())

if __name__ == "__main__":
    build()
