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


def send(text: str, to_user: str | None = None, to_chat: str | None = None) -> None:
    """Ответ туда же, откуда пришла команда: в личку или в чат."""
    try:
        # подтверждения всегда в личку тому, кто отправил команду
        if to_user:
            max_client.send_user(to_user, text)
        else:
            print("нет автора команды — подтверждение не отправлено")
    except Exception as e:  # noqa: BLE001
        print(f"MAX отправка ошибка: {e}")


INSTRUCTION = """📌 ГДЕ И КАК ОТВЕЧАТЬ НА ЗАЯВКИ

1. Карточка заявки приходит в общий чат «Заявки».
2. Ответ пишем в ЛИЧНЫЙ чат с ботом «Заявки SilwerSongFlowers»: из общего чата команды до бота не доходят.
3. Формат: номер заявки, пробел, текст.
   u2i-ag_9dPqu7pxf2Q9YUPvjOA Здравствуйте! Забронировал на 28 ноября.
4. Бот ответит здесь же: «✅ Отправлено в Авито ✅» или «⚠️ Не отправлено» с причиной.
5. Цена зависит от состава, доставка от 500 ₽, один вопрос, ответ до 15 минут, скидка 10% только на «МАМА»."""


def clean(text: str) -> str:
    """Убираем упоминания бота в начале: «@id… текст» → «текст»."""
    return re.sub(r"^(?:@\S+\s+)+", "", text.strip())


def handle(text: str, to_user: str | None = None, to_chat: str | None = None, who: str = "сотрудник") -> bool:
    text = clean(text)
    if text.strip().lower().startswith("#инструкция"):
        send(INSTRUCTION, to_user, to_chat)
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
        send(f"✅ Отправлено в {where} ✅ · заявка {channel[:12]}…\n{body[:200]}", to_user, to_chat)
        # копия в общий чат, чтобы команда видела, кто ответил
        try:
            max_client.send(our_chat(), f"✅ {who} · ответ в {where}\n{body[:220]}")
        except Exception as e:  # noqa: BLE001
            print("не удалось уведомить общий чат:", e)
    else:
        reason = (proc.stdout or proc.stderr or "нет ответа скрипта").strip()[:200]
        send(f"⚠️ Не отправлено в {where} · {channel[:12]}…\n{reason}", to_user, to_chat)
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
        chat_id_value = chat.get("chat_id")
        if chat_id_value is not None and str(chat_id_value) != our_chat():
            continue
        if sender.get("is_bot"):
            continue
        print(f"входящее: {body[:120]!r}")
        sender_id = str((sender.get("user_id") or "")) or None
        sender_name = (sender.get("first_name") or sender.get("name") or "сотрудник")
        if handle(body, to_user=(sender_id if chat_id_value is None else None),
                  to_chat=(str(chat_id_value) if chat_id_value is not None else None),
                  who=sender_name):
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
