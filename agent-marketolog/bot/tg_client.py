# -*- coding: utf-8 -*-
"""Отправка сообщений в Telegram владельцу тем же ботом, что у Котика.

Токен: ~/.claude/channels/telegram/.env (TELEGRAM_BOT_TOKEN)
Получатель: ~/.claude/channels/telegram/access.json → allowFrom[0]

Использование:
    python3 agent-marketolog/bot/tg_client.py "текст"
"""
from __future__ import annotations

import json
import pathlib
import sys
import urllib.parse
import urllib.request

ENV = pathlib.Path.home() / ".claude" / "channels" / "telegram" / ".env"
ACCESS = pathlib.Path.home() / ".claude" / "channels" / "telegram" / "access.json"


def token() -> str:
    for line in ENV.read_text().splitlines():
        if line.startswith("TELEGRAM_BOT_TOKEN="):
            return line.split("=", 1)[1].strip()
    raise RuntimeError("нет TELEGRAM_BOT_TOKEN")


GROUP = pathlib.Path.home() / ".claude" / "channels" / "telegram" / "group.json"


def chat_id() -> str:
    """Если создана группа «Заявки» — шлём туда, иначе в личный чат."""
    if GROUP.exists():
        try:
            gid = json.loads(GROUP.read_text()).get("chat_id")
            if gid:
                return str(gid)
        except Exception:
            pass
    data = json.loads(ACCESS.read_text())
    allow = data.get("allowFrom") or []
    if not allow:
        raise RuntimeError("нет allowFrom в access.json")
    return str(allow[0])


def send(text: str, chat: str | None = None) -> None:
    data = urllib.parse.urlencode({
        "chat_id": chat or chat_id(),
        "text": text,
        "disable_web_page_preview": "true",
    }).encode()
    url = f"https://api.telegram.org/bot{token()}/sendMessage"
    with urllib.request.urlopen(urllib.request.Request(url, data=data), timeout=20) as r:
        body = json.loads(r.read())
    if not body.get("ok"):
        raise RuntimeError(body.get("description", "telegram error"))


if __name__ == "__main__":
    text = sys.argv[1] if len(sys.argv) > 1 else "Проверка связи: заявки подключены."
    send(text)
    print("отправлено в Telegram")
