# -*- coding: utf-8 -*-
"""Отправляет ответ клиенту ВКонтакте от имени сообщества.

Токен: ~/.config/vk-bot/token (ключ доступа сообщества, право «сообщения»)
Номер сообщества: ~/.config/vk-bot/group_id (например 188108705)

    python3 otdel-prodazh/tools/vk-reply.py <peer_id> "текст"
    python3 otdel-prodazh/tools/vk-reply.py --dry <peer_id> "текст"
"""
from __future__ import annotations

import json
import pathlib
import random
import sys
import urllib.parse
import urllib.request

CFG = pathlib.Path.home() / ".config" / "vk-bot"
API = "https://api.vk.com/method/messages.send"
V = "5.199"


def read(name: str) -> str:
    p = CFG / name
    if not p.exists():
        raise SystemExit(f"нет файла {p}")
    return p.read_text().strip()


def send(peer: str, text: str) -> dict:
    params = {
        "peer_id": peer,
        "message": text,
        "random_id": str(random.randint(1, 2**31 - 1)),
        "access_token": read("token"),
        "v": V,
    }
    url = API + "?" + urllib.parse.urlencode(params)
    with urllib.request.urlopen(url, timeout=25) as r:
        return json.loads(r.read())


def main() -> int:
    args = sys.argv[1:]
    dry = "--dry" in args
    if dry:
        args.remove("--dry")
    if len(args) < 2:
        print(__doc__)
        return 2
    peer, text = args[0], args[1]
    if dry:
        print(f"[dry] отправил бы клиенту {peer}: {text[:80]}…")
        return 0
    try:
        data = send(peer, text)
    except SystemExit as e:
        print("ОШИБКА", e)
        return 3
    if "error" in data:
        print("ОШИБКА", data["error"].get("error_msg", "vk error"))
        return 1
    print("ОТПРАВЛЕНО", data.get("response"))
    return 0


if __name__ == "__main__":
    sys.exit(main())
