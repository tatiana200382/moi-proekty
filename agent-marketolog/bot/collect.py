"""Сбор заявок с площадок в один формат и отправка карточек в MAX.

    python3 collect.py yandex            # собрать, сохранить, положить карточки в outbox
    python3 collect.py yandex --send     # собрать и отправить новые в MAX
    python3 collect.py yandex --all      # первый запуск: считать все заявки новыми
    python3 collect.py flush             # отправить всё, что ещё не ушло в MAX
    python3 collect.py status            # что собрано, есть ли токен и чат

Первый обычный запуск не отправляет историю: старые заявки сохраняются со
статусом «старая», чтобы чат не получил десять карточек за прошлый месяц.
Новыми считаются только те, что появились после первого запуска.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import subprocess
import sys
import time
from datetime import datetime, timedelta

import max_client
from lead import LEADS_DIR, MSK, OUTBOX_DIR, Lead, load_all, now_msk

BOT_DIR = os.path.dirname(os.path.abspath(__file__))
CONFIG_PATH = os.path.join(BOT_DIR, "config.json")
STATE_PATH = os.path.join(LEADS_DIR, ".collect-state.json")

MONTHS = {
    "января": 1, "февраля": 2, "марта": 3, "апреля": 4, "мая": 5, "июня": 6,
    "июля": 7, "августа": 8, "сентября": 9, "октября": 10, "ноября": 11, "декабря": 12,
}


def load_config():
    with open(CONFIG_PATH, encoding="utf-8") as f:
        return json.load(f)


def load_state():
    if os.path.exists(STATE_PATH):
        try:
            with open(STATE_PATH, encoding="utf-8") as f:
                return json.load(f)
        except (OSError, ValueError):
            pass
    return {"started_at": None, "sources": {}}


def save_state(state):
    os.makedirs(LEADS_DIR, exist_ok=True)
    with open(STATE_PATH, "w", encoding="utf-8") as f:
        json.dump(state, f, ensure_ascii=False, indent=1)


def run_source(name, cfg):
    """Выполняет sources/<name>.js в управляемом Chrome и возвращает JSON."""
    node = shutil.which("node")
    if not node:
        raise RuntimeError("не найден node — нужен для управления Chrome")
    script = os.path.join(BOT_DIR, "sources", f"{name}.js")
    cmd = [node, os.path.join(BOT_DIR, "browser.mjs"), "run", script,
           cfg["url"], cfg.get("wait_for", "")]
    try:
        proc = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
    except subprocess.TimeoutExpired:
        raise RuntimeError(f"{name}: Chrome не ответил за 120 секунд")
    if proc.returncode != 0:
        detail = (proc.stderr or proc.stdout).strip().splitlines()
        raise RuntimeError(f"{name}: {detail[-1] if detail else 'неизвестная ошибка'}")
    if proc.stderr.strip():
        print(proc.stderr.strip(), file=sys.stderr)
    try:
        return json.loads(proc.stdout)
    except ValueError:
        raise RuntimeError(f"{name}: браузер вернул не JSON: {proc.stdout[:200]}")


def parse_date(text, now):
    """«03 ноября, вт, 22:31» → datetime по Москве. Год — последний, когда дата уже наступила."""
    m = re.search(r"(\d{1,2})\s+([а-яё]+).*?(\d{1,2}):(\d{2})", text.lower())
    if not m:
        return None
    day, month_name, hour, minute = int(m.group(1)), m.group(2), int(m.group(3)), int(m.group(4))
    month = MONTHS.get(month_name)
    if not month:
        return None
    try:
        dt = datetime(now.year, month, day, hour, minute, tzinfo=MSK)
    except ValueError:
        return None
    if dt > now + timedelta(days=1):
        try:
            dt = dt.replace(year=now.year - 1)
        except ValueError:
            return None
    return dt


def client_name(cell):
    lines = [line.strip() for line in cell.splitlines() if line.strip()]
    for line in lines:
        if re.search(r"№|\d{1,2}:\d{2}", line) or len(line) < 2:
            continue
        return line
    return "Клиент"


def parse_items(cell):
    items, amount = [], ""
    for line in cell.splitlines():
        line = line.strip()
        if not line:
            continue
        if "Итого" in line:
            m = re.search(r"([\d\s\u00a0]+)\s*₽", line)
            if m:
                amount = f"{m.group(1).strip()} ₽"
            continue
        m = re.match(r"(\d+)\s*×\s*(.+?)\s+([\d\s\u00a0]+)\s*₽$", line)
        if m:
            title = re.sub(r"\s+", " ", m.group(2)).strip()
            items.append(f"{m.group(1)} × {title} — {m.group(3).strip()} ₽")
    if not amount and items:
        m = re.search(r"([\d\s\u00a0]+)\s*₽$", items[-1])
        if m:
            amount = f"{m.group(1).strip()} ₽"
    return items, amount


def draft_answer(order):
    first = order.client.split()[0] if order.client and order.client != "Клиент" else ""
    hello = f"Здравствуйте, {first}!" if first else "Здравствуйте!"
    titles = []
    for item in order.items:
        title = re.sub(r"^\d+\s*×\s*", "", item)
        title = title.split(" — ")[0].strip()
        titles.append(title)
    what = ", ".join(titles) if titles else "ваш заказ"
    total = f" на {order.amount}" if order.amount else ""
    return (
        f"{hello} Спасибо за заказ № {order.external_id}: {what}{total}. "
        f"Подтвердите, пожалуйста, дату и время — вам удобнее забрать в магазине или привезти? "
        f"Наш телефон: {CONFIG['yandex']['phone']}."
    )


def parse_yandex(payload):
    cfg = CONFIG["yandex"]
    now = now_msk()
    orders = []
    for row in payload.get("rows", []):
        cells = row.get("cells") or []
        if len(cells) < 4:
            continue
        client_cell, item_cell, contact_cell, comment_cell = cells[:4]
        rid = re.search(r"№\s*(\d+)", client_cell)
        if not rid:
            continue
        created = parse_date(client_cell, now)
        if not created:
            continue
        contact_lines = [line.strip() for line in contact_cell.splitlines() if line.strip()]
        phone = next((line for line in contact_lines
                      if re.search(r"(\+7|8)[\d\s()\-]{9,}", line)), "")
        email = next((line for line in contact_lines if "@" in line), "")
        items, amount = parse_items(item_cell)
        comment = re.sub(r"\s+", " ", comment_cell).strip()
        order = Lead(
            source="yandex",
            client=client_name(client_cell),
            question="Заказ с Яндекс.Карт" if items else "Заявка с Яндекс.Карт",
            status="новая",
            created=created.isoformat(timespec="seconds"),
            link=cfg["link"],
            external_id=rid.group(1),
            contact=phone,
            email=email,
            amount=amount,
            items=items,
            comment=comment,
        )
        order.answer = draft_answer(order)
        orders.append(order)
    orders.sort(key=lambda x: x.created, reverse=True)
    return orders


def collect_yandex(verbose=True):
    cfg = CONFIG["yandex"]
    if not cfg.get("enabled"):
        return []
    payload = run_source("yandex", cfg)
    if not payload.get("rows"):
        raise RuntimeError("список заявок пуст — вероятно, сессия Яндекса истекла, проверьте вход")
    orders = parse_yandex(payload)
    if verbose:
        print(f"Яндекс.Карты: в списке {len(payload.get('rows', []))} строк, разобрано заявок {len(orders)}")
    return orders


def collect_avito(verbose=True):
    cfg = CONFIG["avito"]
    if not cfg.get("enabled"):
        if verbose:
            print(f"Авито: выключено — {cfg.get('note', 'нет настроек')}")
        return []
    allowed = [title.lower() for title in cfg.get("allow_item_titles", []) if title]
    if not allowed:
        if verbose:
            print("Авито: не задан список объявлений магазина (allow_item_titles) — пропускаю")
        return []
    payload = run_source("avito", cfg)
    chats = [c for c in payload.get("chats", [])
             if any(title in (c.get("item") or "").lower() for title in allowed)]
    if verbose:
        print(f"Авито: чатов {len(payload.get('chats', []))}, по объявлениям магазина {len(chats)}")
    # В список чатов не входит история переписки, поэтому заявку пока не собираем.
    # Включим разбор сообщений, когда на Авито появятся объявления магазина.
    return []


def collect_vk(verbose=True):
    cfg = CONFIG["vk"]
    if not cfg.get("enabled"):
        if verbose:
            print(f"ВКонтакте: выключено — {cfg.get('note', 'нет настроек')}")
        return []
    payload = run_source("vk", cfg)
    if not payload.get("enabled", True):
        if verbose:
            print("ВКонтакте: в сообществе выключены сообщения — заявок нет")
        return []
    if verbose:
        print(f"ВКонтакте: диалогов {len(payload.get('chats', []))}")
    return []


COLLECTORS = {"yandex": collect_yandex, "avito": collect_avito, "vk": collect_vk}


def existing_keys():
    return {order.key for order in load_all() if order.key}


def queue_card(order):
    os.makedirs(OUTBOX_DIR, mode=0o700, exist_ok=True)
    os.chmod(OUTBOX_DIR, 0o700)
    path = os.path.join(OUTBOX_DIR, order.filename().replace(".json", ".txt"))
    with open(path, "w", encoding="utf-8") as f:
        f.write(order.card() + "\n")
    os.chmod(path, 0o600)
    return path


def send_order(order):
    cid = CONFIG["max"].get("chat_id") or max_client.chat_id()
    response = max_client.send(cid, order.card())
    try:
        mid = response["message"]["body"]["mid"]
    except (KeyError, TypeError):
        mid = ""
    order.notified = True
    order.status = "отправлена"
    order.sent_at = now_msk().isoformat(timespec="seconds")
    order.max_mid = str(mid)
    order.save()
    queued = os.path.join(OUTBOX_DIR, order.filename().replace(".json", ".txt"))
    if os.path.exists(queued):
        os.remove(queued)
    return mid


def handle_new(orders, send):
    known = existing_keys()
    fresh = [o for o in orders if o.key not in known]
    if not fresh:
        print("Новых заявок нет.")
        return 0
    for order in fresh:
        order.save()
        queue_card(order)
        print(f"  + {order.created[:16]} {order.source} №{order.external_id} · {order.client} · {order.amount or 'без суммы'}")
    if not send:
        print(f"Сохранено {len(fresh)}, карточки в {OUTBOX_DIR}. Отправка: добавьте --send.")
        return len(fresh)
    if not max_client.token_exists():
        print("Токен MAX не найден — карточки лежат в outbox, отправка не выполнена.")
        return len(fresh)
    try:
        CONFIG["max"]["chat_id"] = CONFIG["max"].get("chat_id") or max_client.chat_id()
    except max_client.MaxError as e:
        print(f"Чат MAX не настроен: {e}. Карточки лежат в outbox.")
        return len(fresh)
    sent = 0
    for order in fresh:
        try:
            mid = send_order(order)
            sent += 1
            print(f"  → MAX: №{order.external_id} (mid {mid or '—'})")
            time.sleep(0.6)
        except max_client.MaxError as e:
            print(f"  ! MAX: №{order.external_id}: {e}")
            break
    return sent


def flush():
    pending = [o for o in load_all() if o.status == "новая" and not o.notified]
    if not pending:
        print("Нечего отправлять.")
        return 0
    if not max_client.token_exists():
        print(f"Токен MAX не найден. Неотправленных карточек: {len(pending)}")
        return 0
    try:
        cid = CONFIG["max"].get("chat_id") or max_client.chat_id()
    except max_client.MaxError as e:
        print(f"Чат MAX не настроен: {e}")
        return 0
    sent = 0
    for order in pending:
        try:
            mid = send_order(order)
            sent += 1
            print(f"→ MAX: {order.source} №{order.external_id} (mid {mid or '—'})")
            time.sleep(0.6)
        except max_client.MaxError as e:
            print(f"! MAX: {order.source} №{order.external_id}: {e}")
            break
    print(f"Отправлено: {sent} из {len(pending)}")
    return sent


def print_status():
    orders = load_all()
    by_source = {}
    by_status = {}
    for order in orders:
        by_source[order.source] = by_source.get(order.source, 0) + 1
        by_status[order.status] = by_status.get(order.status, 0) + 1
    state = load_state()
    outbox = len([n for n in os.listdir(OUTBOX_DIR) if n.endswith(".txt")]) if os.path.isdir(OUTBOX_DIR) else 0
    print(f"Заявок в базе: {len(orders)}")
    print("  по площадкам:", ", ".join(f"{k} {v}" for k, v in sorted(by_source.items())) or "—")
    print("  по статусам:", ", ".join(f"{k} {v}" for k, v in sorted(by_status.items())) or "—")
    print(f"Карточек в outbox: {outbox}")
    print(f"Токен MAX: {'есть' if max_client.token_exists() else 'нет'}")
    has_chat = os.path.exists(max_client.CHAT_FILE) or os.path.exists(max_client.LOCAL_CHAT_FILE)
    print(f"ID чата MAX: {'есть' if has_chat else 'нет'}")
    print(f"Первый запуск: {state.get('started_at') or 'ещё не было'}")
    for name, value in sorted((state.get("sources") or {}).items()):
        print(f"  {name}: последний сбор {value}")


def main():
    global CONFIG
    parser = argparse.ArgumentParser(description="Сбор заявок в MAX")
    parser.add_argument("source", choices=["yandex", "avito", "vk", "all", "flush", "status"])
    parser.add_argument("--send", action="store_true", help="отправить новые карточки в MAX")
    parser.add_argument("--all", action="store_true", help="первый запуск: все заявки считать новыми")
    args = parser.parse_args()

    CONFIG = load_config()
    if args.source == "status":
        print_status()
        return
    if args.source == "flush":
        flush()
        return

    names = ["yandex", "avito", "vk"] if args.source == "all" else [args.source]
    orders = []
    failed = set()
    for name in names:
        try:
            orders.extend(COLLECTORS[name]())
        except (RuntimeError, OSError) as e:
            failed.add(name)
            print(f"{name}: ошибка — {e}", file=sys.stderr)

    baseline = load_state().get("started_at") is None and not args.all
    if baseline and "yandex" in failed and args.source in ("yandex", "all"):
        print("Первый запуск не выполнен: Яндекс не отдал список. Состояние не меняю.")
        return
    if baseline and not orders:
        print("Первый запуск не выполнен: заявок нет. Состояние не меняю.")
        return
    if baseline:
        known = existing_keys()
        fresh = [o for o in orders if o.key not in known]
        for order in fresh:
            order.status = "старая"
            order.baseline = True
            order.save()
        state = load_state()
        state["started_at"] = now_msk().isoformat(timespec="seconds")
        state["sources"] = {name: now_msk().isoformat(timespec="seconds") for name in names}
        save_state(state)
        print(f"Первый запуск: {len(fresh)} заявок сохранены как история, в MAX не отправлялись.")
        print("Следующие запуски будут присылать только новые. Все сразу: --all.")
        return

    if failed:
        print(f"Не все источники отработали: {', '.join(sorted(failed))} — смотрите ошибки выше.")
    sent = handle_new(orders, args.send)
    state = load_state()
    state["sources"] = {name: now_msk().isoformat(timespec="seconds") for name in names}
    save_state(state)
    if sent and args.send:
        print(f"Отправлено в MAX: {sent}")


CONFIG = load_config()

if __name__ == "__main__":
    main()
