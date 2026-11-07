"""Клиент MAX Bot API. Токен — только в файле вне проекта.

Токен: ~/.config/max-bot/token (одна строка). Права 600.
Проверка: python3 max_client.py me
"""
import json
import os
import sys
import urllib.error
import urllib.request

BASE = "https://platform-api2.max.ru"
TOKEN_FILE = os.path.expanduser("~/.config/max-bot/token")


def token():
    if not os.path.exists(TOKEN_FILE):
        raise SystemExit(f"нет файла с токеном: {TOKEN_FILE}")
    with open(TOKEN_FILE, encoding="utf-8") as f:
        value = f.read().strip()
    if len(value) < 10:
        raise SystemExit("токен пустой или слишком короткий")
    return value


def call(method, path, payload=None):
    data = json.dumps(payload).encode() if payload is not None else None
    req = urllib.request.Request(
        BASE + path,
        data=data,
        method=method,
        headers={
            "Authorization": token(),
            "Content-Type": "application/json",
        },
    )
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            body = resp.read().decode()
            return json.loads(body) if body else {}
    except urllib.error.HTTPError as e:
        detail = e.read().decode()[:300]
        raise SystemExit(f"MAX API {e.code}: {detail}")


def me():
    return call("GET", "/me")


def send(chat_id, text):
    return call("POST", "/messages", {"chat_id": chat_id, "text": text})


def updates(limit=20):
    return call("GET", f"/updates?limit={limit}")


def main():
    cmd = sys.argv[1] if len(sys.argv) > 1 else "me"
    if cmd == "me":
        print(json.dumps(me(), ensure_ascii=False, indent=1))
    elif cmd == "send" and len(sys.argv) >= 4:
        print(json.dumps(send(sys.argv[2], sys.argv[3]), ensure_ascii=False)[:300])
    elif cmd == "updates":
        print(json.dumps(updates(), ensure_ascii=False)[:800])
    else:
        print("команды: me | send <chat_id> <текст> | updates")


if __name__ == "__main__":
    main()
