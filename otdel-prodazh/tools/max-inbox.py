# -*- coding: utf-8 -*-
"""Принимает ответы сотрудников из чата MAX «Заявки» и отправляет их в Авито.

Формат сообщения сотрудника:
    #u2i-xEx2... ответ: Здравствуйте! Подберу вариант до 3 500 ₽.

    python3 otdel-prodazh/tools/max-inbox.py          # один проход
    python3 otdel-prodazh/tools/max-inbox.py --watch  # опрос каждые 20 секунд
"""
from __future__ import annotations

import json
import os
import pathlib
import re
import subprocess
import sys
import time

ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "agent-marketolog" / "bot"))

import max_client  # noqa: E402

STATE = ROOT / "otdel-prodazh" / "runtime" / "max-inbox.json"
REPLY = ROOT / "otdel-prodazh" / "tools" / "avito-reply.py"
VK_REPLY = ROOT / "otdel-prodazh" / "tools" / "vk-reply-browser.py"
PATTERN = re.compile(r"^#?([A-Za-z0-9_~\-]{6,})\s*(?:ответ|otvet)?\s*[:\-]?\s*(.+)$", re.I | re.S)


def our_chat() -> str:
    return str(max_client.chat_id())


def load_state() -> dict:
    if STATE.exists():
        try:
            return json.loads(STATE.read_text())
        except Exception:
            pass
    return {}


def save_state(state: dict) -> None:
    STATE.parent.mkdir(parents=True, exist_ok=True)
    STATE.write_text(json.dumps(state, ensure_ascii=False, indent=2))


def send(text: str) -> None:
    try:
        max_client.send(our_chat(), text)
    except Exception as e:  # noqa: BLE001
        print(f"MAX отправка ошибка: {e}")


INSTRUCTION = """📌 КАК ОТВЕТИТЬ НА ЗАЯВКУ

Пишите в этот чат одной строкой:
#номер ответ: текст

Пример:
#u2i-xEx2zqdyoJnr8ewagY8RGA ответ: Здравствуйте! Букет на 29 ноября есть, пришлём фото.

Где взять номер: последняя строка карточки заявки, после решётки.
u2i-… — Авито, просто цифры — ВКонтакте.

Что будет: бот отправит текст клиенту и пришлёт сюда «✅ Ответ отправлен» с копией.

Правила:
1. Цену букета не называем — зависит от состава.
2. Доставка от 500 ₽, точная сумма по адресу.
3. Один вопрос за сообщение.
4. Ответ до 15 минут с 9:00 до 22:00.
5. Скидка 10% только на слово «МАМА» и только на предзаказ."""


def handle(text: str) -> bool:
    if text.strip().lower().startswith("#инструкция"):
        send(INSTRUCTION)
        print("OK инструкция")
        return True
    m = PATTERN.match(text.strip())
    if not m:
        return False
    channel, body = m.group(1), m.group(2).strip()
    is_vk = channel.isdigit()
    script = VK_REPLY if is_vk else REPLY
    env = dict(os.environ, NO_MAX_LOG="1")
    proc = subprocess.run([sys.executable, str(script), channel, body],
                          capture_output=True, text=True, timeout=150, env=env)
    where = "ВКонтакте" if is_vk else "Авито"
    ok = proc.returncode == 0 and "ОТПРАВЛЕНО" in (proc.stdout or "")
    if ok:
        send(f"✅ Отправлено в {where} · заявка {channel[:12]}…")
    else:
        reason = (proc.stdout or proc.stderr or "нет ответа скрипта").strip()[:200]
        send(f"⚠️ Не отправлено в {where} · {channel[:12]}…\n{reason}")
    print(("OK " if ok else "FAIL ") + channel)
    return True


def once() -> int:
    state = load_state()
    marker = state.get("marker")
    data = max_client.updates(marker=marker, timeout=3)
    updates = data.get("updates", [])
    handled = 0
    for u in updates:
        msg = u.get("message") or {}
        chat = msg.get("chat") or {}
        body = (msg.get("body") or {}).get("text") or ""
        sender = (msg.get("sender") or {})
        if str(chat.get("chat_id")) != our_chat():
            continue
        if sender.get("is_bot"):
            continue
        print(f"входящее: {body[:120]!r}")
        if handle(body):
            handled += 1
    if data.get("marker"):
        state["marker"] = data["marker"]
    save_state(state)
    print(f"апдейтов: {len(updates)}, ответов обработано: {handled}")
    return handled


def main() -> int:
    if "--watch" in sys.argv:
        while True:
            try:
                once()
            except Exception as e:  # noqa: BLE001
                print("ошибка опроса:", e)
            time.sleep(20)
    return 0 if once() >= 0 else 1


if __name__ == "__main__":
    sys.exit(main())
