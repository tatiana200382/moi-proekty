#!/usr/bin/env python3
"""Отдел продаж: заявки → карточки заявок → MAX → отчёт.

Что делает:
  * читает заявки, которые собрал бот Вовы (agent-marketolog/leads/);
  * проверяет, хватает ли данных для работы (контакт, состав, сумма);
  * делит на «готовые» (A), «нужно уточнить» (B) и «не заявка» (C);
  * отправляет владельцу в MAX карточки заявок с действием и дедлайном;
  * дважды в день присылает короткий итог, в пятницу — итог недели;
  * считает результат: заказы, выручку, потери, просрочки.

Клиентам ничего не отправляет. Автоответы — только черновиком в карточке.

Запуск:
  python3 otdel-prodazh/tools/sales_pipeline.py --sync
  python3 otdel-prodazh/tools/sales_pipeline.py --send
  python3 otdel-prodazh/tools/sales_pipeline.py --digest
  python3 otdel-prodazh/tools/sales_pipeline.py --weekly
  python3 otdel-prodazh/tools/sales_pipeline.py --auto
  python3 otdel-prodazh/tools/sales_pipeline.py --status
  python3 otdel-prodazh/tools/sales_pipeline.py --mark yandex:1494024 order --amount 3200
  python3 otdel-prodazh/tools/sales_pipeline.py --demo
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import os
import subprocess
import sys
from datetime import datetime, timedelta, timezone

MSK = timezone(timedelta(hours=3))
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
SALES_DIR = os.path.join(ROOT, "otdel-prodazh")
SOURCE_DIR = os.path.join(ROOT, "agent-marketolog", "leads")
RUNTIME = os.path.join(SALES_DIR, "runtime")
STATE_FILE = os.path.join(RUNTIME, "state.json")
CSV_FILE = os.path.join(RUNTIME, "zayavki.csv")
LOG_FILE = os.path.join(RUNTIME, "logs", "pipeline.log")
OUTBOX = os.path.join(RUNTIME, "outbox")
MAX_CLIENT = os.path.join(ROOT, "agent-marketolog", "bot", "max_client.py")

SOURCE_NAMES = {"yandex": "Яндекс.Карты", "vk": "ВКонтакте", "avito": "Авито"}
ICONS = {"A": "🔥", "B": "🟡", "C": "⚪"}

CSV_FIELDS = [
    "id", "created", "source", "client", "contact", "readiness", "status",
    "amount", "action", "deadline", "sent_at", "notes",
]


def now() -> datetime:
    return datetime.now(MSK)


def iso(dt: datetime) -> str:
    return dt.isoformat(timespec="seconds")


def parse_dt(value: str):
    try:
        dt = datetime.fromisoformat(value)
    except (TypeError, ValueError):
        return None
    return dt if dt.tzinfo else dt.replace(tzinfo=MSK)


def fmt_dt(value: str) -> str:
    dt = parse_dt(value)
    return dt.strftime("%d.%m.%Y %H:%M") if dt else (value or "—")


def log(message: str) -> None:
    os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(f"{iso(now())} {message}\n")


def load_state() -> dict:
    if not os.path.exists(STATE_FILE):
        return {"version": 1, "leads": {}, "digests": {}, "weekly": {}, "last_run": ""}
    try:
        with open(STATE_FILE, encoding="utf-8") as f:
            data = json.load(f)
        data.setdefault("leads", {})
        data.setdefault("digests", {})
        data.setdefault("weekly", {})
        return data
    except (OSError, ValueError):
        log("state.json битый — начинаю новый")
        return {"version": 1, "leads": {}, "digests": {}, "weekly": {}, "last_run": ""}


def save_state(state: dict) -> None:
    os.makedirs(RUNTIME, mode=0o700, exist_ok=True)
    tmp = STATE_FILE + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(state, f, ensure_ascii=False, indent=1)
    os.chmod(tmp, 0o600)
    os.replace(tmp, STATE_FILE)


def source_leads() -> list:
    leads = []
    if not os.path.isdir(SOURCE_DIR):
        return leads
    for name in sorted(os.listdir(SOURCE_DIR)):
        if not name.endswith(".json") or name.startswith("."):
            continue
        try:
            with open(os.path.join(SOURCE_DIR, name), encoding="utf-8") as f:
                data = json.load(f)
            if not isinstance(data, dict) or not data.get("source"):
                continue
            data["_file"] = name
            leads.append(data)
        except (OSError, ValueError):
            log(f"битый файл заявки пропущен: {name}")
    return leads


def lead_key(d: dict) -> str:
    ext = str(d.get("external_id") or "").strip()
    if ext:
        return f"{d.get('source','?')}:{ext}"
    raw = f"{d.get('source')}|{d.get('client')}|{d.get('created')}"
    return f"{d.get('source','?')}:{hashlib.sha1(raw.encode()).hexdigest()[:10]}"


PLACEHOLDER_PHONES = {"+7 900 000-00-00", "8 900 000-00-00", "000-00-00", "+7 000 000-00-00"}


def _digits(value: str) -> str:
    return "".join(ch for ch in value if ch.isdigit())


def has_contact(d: dict) -> bool:
    """Контакт годен, если это почта или телефон нормального вида, а не заглушка."""
    email = (d.get("email") or "").strip()
    if "@" in email and "." in email.split("@")[-1]:
        return True
    phone = (d.get("contact") or "").strip()
    if not phone:
        return False
    if phone in PLACEHOLDER_PHONES or "000-00-00" in phone:
        return False
    digits = _digits(phone)
    if len(digits) < 10:
        return False
    if len(set(digits)) <= 2:          # 0000000000, 1111111111
        return False
    return True


def has_order(d: dict) -> bool:
    if d.get("items") or (d.get("amount") or "").strip():
        return True
    return "заказ" in (d.get("question") or "").lower()


def is_test(d: dict) -> bool:
    """Тест и демо не должны попадать в боевую воронку."""
    client = (d.get("client") or "").lower()
    question = (d.get("question") or "").lower()
    contact = (d.get("contact") or "").lower()
    if client in {"test user", "тест", "test"} or "test user" in client:
        return True
    if "demo" in client or "демо" in client or "демо" in question:
        return True
    if contact in {p.lower() for p in PLACEHOLDER_PHONES} or "000-00-00" in contact:
        return True
    # заявка без внешнего id и без ссылки из чат-источника — почти всегда демо
    if d.get("source") in {"avito", "vk", "telegram"} and not str(d.get("external_id") or "").strip() and not str(d.get("link") or "").strip():
        return True
    return False


def qualify(d: dict) -> dict:
    """A — готовая, B — нужно уточнить, C — не заявка."""
    contact = has_contact(d)
    order = has_order(d)
    missing = []
    if not contact:
        missing.append("телефон")
    if not d.get("items"):
        missing.append("состав")
    if not (d.get("amount") or "").strip():
        missing.append("сумма")
    if not (d.get("comment") or "").strip():
        missing.append("дата/время/адрес")

    if is_test(d):
        return {"code": "C", "why": "тестовая запись", "missing": [], "action": "ничего не делать"}
    if not contact and not order:
        return {"code": "C", "why": "нет контакта и нет заказа", "missing": missing,
                "action": "проверить источник вручную"}
    if not contact:
        return {"code": "C", "why": "нет пригодного контакта (заглушка или неполный номер)",
                "missing": missing, "action": "проверить диалог в источнике вручную"}
    if contact and order:
        return {"code": "A", "why": "есть контакт и заказ", "missing": missing,
                "action": "позвонить, подтвердить дату, время и адрес; сверить состав"}
    if contact:
        return {"code": "B", "why": "есть контакт, нет деталей", "missing": missing,
                "action": "задать 2 вопроса: повод/дата и бюджет; взять состав"}
    return {"code": "B", "why": "есть заказ, нет контакта", "missing": missing,
            "action": "написать в источник и запросить телефон"}


def deadline_for(d: dict, q: dict) -> str:
    created = parse_dt(d.get("created") or "")
    base = created if created and created.date() == now().date() else now()
    # регламент отдела: A — 15 минут, B — 2 часа, ночью — до 09:30
    hour = now().hour
    if hour >= 22 or hour < 9:
        value = base.replace(hour=9, minute=30, second=0, microsecond=0) + timedelta(days=1 if hour >= 22 else 0)
        return iso(value)
    delta = timedelta(minutes=15) if q["code"] == "A" else timedelta(hours=2)
    value = base + delta
    if value < now():
        value = now() + timedelta(minutes=30)
    return iso(value)


def render_card(entry: dict) -> str:
    q = entry["readiness"]
    title = "КАРТОЧКА ЗАЯВКИ · готова" if q == "A" else "КАРТОЧКА ЗАЯВКИ · уточнить"
    src = SOURCE_NAMES.get(entry["source"], entry["source"])
    lines = [f"{ICONS.get(q, '⚪')} {title} · {src}"]
    if entry.get("external_id"):
        lines.append(f"№ {entry['external_id']} · {fmt_dt(entry['created'])}")
    else:
        lines.append(f"Время: {fmt_dt(entry['created'])}")
    lines.append(f"Клиент: {entry['client'] or '—'}")
    if entry.get("contact"):
        lines.append(f"Телефон: {entry['contact']}")
    if entry.get("email"):
        lines.append(f"Почта: {entry['email']}")
    if entry.get("items"):
        lines.append("Что нужно:")
        lines.extend(f"• {item}" for item in entry["items"][:5])
    elif entry.get("question"):
        lines.append(f"Запрос: {entry['question']}")
    if entry.get("amount"):
        lines.append(f"Сумма: {entry['amount']}")
    if entry.get("comment"):
        lines.append(f"Комментарий: {entry['comment']}")
    if entry.get("missing"):
        lines.append(f"Чего не хватает: {', '.join(entry['missing'])}")
    lines.append(f"Действие: {entry['action']}")
    lines.append(f"Дедлайн: {fmt_dt(entry['deadline'])}")
    if entry.get("draft"):
        draft = entry["draft"].strip().replace("\n", " ")
        lines.append(f"Черновик ответа: {draft[:350]}")
    if entry.get("link"):
        lines.append(f"Источник: {entry['link']}")
    lines.append(f"ID: {entry['id']}")
    return "\n".join(lines)[:3800]


def sync() -> dict:
    state = load_state()
    added = 0
    for d in source_leads():
        key = lead_key(d)
        if key in state["leads"]:
            continue
        q = qualify(d)
        old = bool(d.get("baseline")) or (d.get("status") == "старая")
        status = "archive" if old else ("new" if q["code"] in ("A", "B") else "skip")
        entry = {
            "id": key,
            "source": d.get("source") or "?",
            "external_id": str(d.get("external_id") or ""),
            "client": (d.get("client") or "").strip(),
            "contact": (d.get("contact") or "").strip(),
            "email": (d.get("email") or "").strip(),
            "created": d.get("created") or iso(now()),
            "question": d.get("question") or "",
            "items": d.get("items") or [],
            "amount": d.get("amount") or "",
            "comment": d.get("comment") or "",
            "link": d.get("link") or "",
            "draft": d.get("answer") or "",
            "readiness": q["code"],
            "why": q["why"],
            "missing": q["missing"],
            "action": q["action"],
            "status": status,
            "deadline": deadline_for(d, q),
            "first_seen": iso(now()),
            "sent_at": "",
            "send_errors": 0,
            "notes": "",
        }
        state["leads"][key] = entry
        added += 1
    state["last_run"] = iso(now())
    save_state(state)
    write_csv(state)
    log(f"sync: добавлено {added}, всего {len(state['leads'])}")
    return state


def write_csv(state: dict) -> None:
    os.makedirs(RUNTIME, mode=0o700, exist_ok=True)
    rows = sorted(state["leads"].values(), key=lambda x: x.get("created", ""), reverse=True)
    tmp = CSV_FILE + ".tmp"
    with open(tmp, "w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=CSV_FIELDS, extrasaction="ignore")
        writer.writeheader()
        for row in rows:
            writer.writerow(row)
    os.replace(tmp, CSV_FILE)


def max_chat() -> str:
    for path in (os.path.expanduser("~/.config/max-bot/chat_id"),
                 os.path.join(ROOT, "agent-marketolog", "bot", "chat_id")):
        if os.path.exists(path):
            with open(path, encoding="utf-8") as f:
                value = f.read().strip()
            if value:
                return value
    raise RuntimeError("нет chat_id MAX")


def max_send(text: str) -> str:
    chat = max_chat()
    result = subprocess.run(
        [sys.executable, MAX_CLIENT, "send", chat, text],
        capture_output=True, text=True, timeout=40,
    )
    if result.returncode != 0:
        raise RuntimeError((result.stderr or result.stdout or "MAX не ответил").strip()[:300])
    return (result.stdout or "").strip()[:300]


def send_text_safe(text: str, tag: str) -> bool:
    try:
        max_send(text)
        log(f"MAX отправлено: {tag}")
        return True
    except Exception as e:  # noqa: BLE001 — сеть/токен/чат, причина в лог
        log(f"MAX ОШИБКА {tag}: {e}")
        os.makedirs(OUTBOX, mode=0o700, exist_ok=True)
        path = os.path.join(OUTBOX, f"{now().strftime('%Y%m%dT%H%M%S')}-{tag}.txt")
        with open(path, "w", encoding="utf-8") as f:
            f.write(text)
        os.chmod(path, 0o600)
        return False


def send_new(limit: int = 5) -> int:
    state = load_state()
    sent = 0
    for entry in sorted(state["leads"].values(), key=lambda x: x.get("created", "")):
        if entry["status"] != "new" or entry["readiness"] not in {"A", "B"}:
            continue
        if sent >= limit:
            break
        if send_text_safe(render_card(entry), entry["id"].replace(":", "-")):
            entry["status"] = "sent"
            entry["sent_at"] = iso(now())
            sent += 1
        else:
            entry["send_errors"] = entry.get("send_errors", 0) + 1
            if entry["send_errors"] >= 5:
                entry["status"] = "send_error"
    save_state(state)
    write_csv(state)
    log(f"send: отправлено {sent}")
    return sent


def active(state: dict, readiness=None) -> list:
    rows = [x for x in state["leads"].values() if x["status"] in ("new", "sent", "in_work")]
    if readiness:
        rows = [x for x in rows if x["readiness"] == readiness]
    return sorted(rows, key=lambda x: x.get("deadline", ""))


def is_overdue(entry: dict) -> bool:
    dl = parse_dt(entry.get("deadline") or "")
    return bool(dl and dl < now() and entry["status"] in ("new", "sent", "in_work"))


def digest_text(state: dict) -> str:
    rows = active(state)
    a = [x for x in rows if x["readiness"] == "A"]
    b = [x for x in rows if x["readiness"] == "B"]
    overdue = [x for x in rows if is_overdue(x)]
    orders = [x for x in state["leads"].values() if x["status"] == "order"]
    lost = [x for x in state["leads"].values() if x["status"] == "lost"]
    revenue = 0
    for x in orders:
        try:
            revenue += int("".join(ch for ch in str(x.get("amount", "")) if ch.isdigit()) or 0)
        except ValueError:
            pass
    lines = [f"📊 Отдел продаж · {now().strftime('%d.%m.%Y, %H:%M')}"]
    lines.append(f"Карточек к действию: {len(a)} · ждут уточнения: {len(b)} · просрочено: {len(overdue)}")
    lines.append(f"Подтверждённых заказов: {len(orders)} · выручка: {revenue:,} ₽".replace(",", " "))
    lines.append(f"Потерь: {len(lost)}")
    if a:
        lines.append("")
        lines.append("Можно звонить:")
        for x in a[:7]:
            who = x["client"] or x["contact"] or x["id"]
            lines.append(f"• {who} · {x.get('amount') or 'сумма не указана'} · до {fmt_dt(x['deadline'])}")
    if overdue:
        lines.append("")
        lines.append("Просрочены:")
        for x in overdue[:5]:
            lines.append(f"• {x['client'] or x['id']} · дедлайн {fmt_dt(x['deadline'])}")
    if not rows:
        lines.append("")
        lines.append("Новых заявок нет. Отдел на связи.")
    return "\n".join(lines)[:3500]


def weekly_text(state: dict) -> str:
    start = now() - timedelta(days=7)
    rows = [
        x for x in state["leads"].values()
        if (parse_dt(x.get("first_seen") or "") or start) >= start
        and x["status"] not in ("archive", "skip", "send_error")
    ]
    orders = [x for x in rows if x["status"] == "order"]
    lost = [x for x in rows if x["status"] == "lost"]
    revenue = 0
    for x in orders:
        try:
            revenue += int("".join(ch for ch in str(x.get("amount", "")) if ch.isdigit()) or 0)
        except ValueError:
            pass
    cr = f"{len(orders) / len(rows) * 100:.0f}%" if rows else "нет данных"
    reasons = {}
    for x in lost:
        reasons[x.get("notes") or "без причины"] = reasons.get(x.get("notes") or "без причины", 0) + 1
    lines = [f"📈 Итог недели · {start.strftime('%d.%m')}–{now().strftime('%d.%m.%Y')}"]
    lines.append(f"Заявок: {len(rows)} · заказов: {len(orders)} · конверсия: {cr}")
    lines.append(f"Выручка: {revenue:,} ₽ · потерь: {len(lost)}".replace(",", " "))
    if orders:
        checks = []
        for x in orders:
            try:
                checks.append(int("".join(ch for ch in str(x.get("amount", "")) if ch.isdigit()) or 0))
            except ValueError:
                pass
        if checks:
            lines.append(f"Средний чек: {sum(checks) // len(checks):,} ₽".replace(",", " "))
    if reasons:
        lines.append("Причины потерь: " + ", ".join(f"{k} — {v}" for k, v in reasons.items()))
    lines.append("")
    lines.append("Следующий шаг: разобрать просрочки и закрыть причины потерь.")
    return "\n".join(lines)[:3500]


def send_digest(slot: str = "manual") -> bool:
    state = load_state()
    key = f"{now().strftime('%Y-%m-%d')}:{slot}"
    if slot != "manual" and key in state["digests"]:
        return True
    ok = send_text_safe(digest_text(state), f"digest-{slot}")
    if ok:
        state["digests"][key] = iso(now())
        save_state(state)
    return ok


def send_weekly() -> bool:
    state = load_state()
    key = now().strftime("%G-W%V")
    if key in state["weekly"]:
        return True
    ok = send_text_safe(weekly_text(state), f"weekly-{key}")
    if ok:
        state["weekly"][key] = iso(now())
        save_state(state)
    return ok


def mark(lead_id: str, status: str, amount: str = "", note: str = "") -> None:
    state = load_state()
    entry = state["leads"].get(lead_id)
    if not entry:
        raise SystemExit(f"нет заявки {lead_id}")
    entry["status"] = status
    if amount:
        entry["amount"] = f"{amount} ₽"
    if note:
        entry["notes"] = note
    save_state(state)
    write_csv(state)
    log(f"mark {lead_id} -> {status} {amount} {note}")


def auto() -> None:
    sync()
    send_new()
    h = now().hour
    today = now().strftime("%Y-%m-%d")
    # Догоняем, если Mac спал в 09:00 или 19:00: итог всё равно уйдёт.
    if h >= 9 and f"{today}:morning" not in load_state().get("digests", {}):
        send_digest("morning")
    if h >= 19 and f"{today}:evening" not in load_state().get("digests", {}):
        send_digest("evening")
    if now().weekday() == 4 and h >= 16:
        send_weekly()


def requalify() -> int:
    """Пересчитать готовность и дедлайн у всех заявок по текущим правилам."""
    state = load_state()
    changed = 0
    for entry in state["leads"].values():
        q = qualify(entry)
        if entry.get("readiness") != q["code"]:
            entry["readiness"] = q["code"]
            entry["action"] = q["action"]
            entry["why"] = q["why"]
            entry["deadline"] = deadline_for(entry, q)
            changed += 1
    save_state(state)
    write_csv(state)
    log(f"requalify: пересчитано {changed}")
    print(f"пересчитано заявок: {changed}")
    return changed


def show_status() -> None:
    state = load_state()
    rows = list(state["leads"].values())
    counts = {}
    for x in rows:
        counts[x["status"]] = counts.get(x["status"], 0) + 1
    print(f"Всего заявок: {len(rows)}")
    for k in ("new", "sent", "in_work", "order", "lost", "archive", "skip", "send_error"):
        if counts.get(k):
            print(f"  {k}: {counts[k]}")
    print(f"Карточек A: {len(active(state, 'A'))} · B: {len(active(state, 'B'))}")
    print(f"Последний запуск: {state.get('last_run') or '—'}")
    print(f"CSV: {CSV_FILE}")


def demo() -> None:
    samples = [
        {
            "id": "demo:1", "source": "yandex", "external_id": "1494024",
            "client": "Елена Братухина", "contact": "+7 911 164 95 99", "email": "",
            "created": iso(now()), "items": ['Букет "Аромат" — 3 200 ₽'], "amount": "3 200 ₽",
            "comment": "Доставка завтра к 12:00", "draft": "Здравствуйте! Подтвердите адрес.",
            "link": "", "readiness": "A", "missing": ["адрес"], "action": "позвонить и подтвердить адрес",
            "deadline": iso(now() + timedelta(hours=2)),
        },
        {
            "id": "demo:2", "source": "vk", "external_id": "",
            "client": "Анна", "contact": "", "email": "", "created": iso(now()),
            "items": [], "amount": "", "comment": "", "question": "Сколько стоит букет на свадьбу?",
            "draft": "", "link": "", "readiness": "B", "missing": ["телефон", "бюджет"],
            "action": "уточнить дату и бюджет", "deadline": iso(now() + timedelta(hours=6)),
        },
    ]
    for s in samples:
        print(render_card(s))
        print("\n" + "—" * 40 + "\n")


def main() -> None:
    p = argparse.ArgumentParser(description="Заявки отдела продаж")
    p.add_argument("--sync", action="store_true", help="прочитать новые заявки")
    p.add_argument("--send", action="store_true", help="отправить готовые в MAX")
    p.add_argument("--digest", action="store_true", help="итог дня в MAX")
    p.add_argument("--weekly", action="store_true", help="итог недели в MAX")
    p.add_argument("--auto", action="store_true", help="sync + send + итоги по расписанию")
    p.add_argument("--requalify", action="store_true", help="пересчитать готовность и дедлайны")
    p.add_argument("--status", action="store_true", help="показать состояние")
    p.add_argument("--demo", action="store_true", help="показать примеры карточек")
    p.add_argument("--preview", action="store_true", help="показать итог дня и недели без отправки")
    p.add_argument("--mark", nargs=2, metavar=("ID", "STATUS"), help="отметить статус заявки")
    p.add_argument("--amount", default="", help="сумма для --mark")
    p.add_argument("--note", default="", help="примечание для --mark")
    args = p.parse_args()

    os.makedirs(RUNTIME, mode=0o700, exist_ok=True)
    if args.demo:
        demo()
    elif args.preview:
        state = load_state()
        print(digest_text(state))
        print("\n" + "=" * 40 + "\n")
        print(weekly_text(state))
    elif args.requalify:
        requalify()
    elif args.mark:
        mark(args.mark[0], args.mark[1], args.amount, args.note)
    elif args.status:
        show_status()
    elif args.auto:
        auto()
    else:
        if args.sync:
            sync()
        if args.send:
            send_new()
        if args.digest:
            send_digest()
        if args.weekly:
            send_weekly()
        if not any((args.sync, args.send, args.digest, args.weekly)):
            p.print_help()


if __name__ == "__main__":
    main()
