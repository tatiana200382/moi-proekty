"""Шаг 3. Список контактов из Telegram.

Для каждого сохранённого аккаунта снимает контакт-лист: имя, юзернейм, телефон.
"""
import asyncio
import json
import sys

from common import TG_DIR, head, load_config, say


def main():
    cfg = load_config()
    tg = cfg["telegram"]
    if not tg.get("enabled", True):
        say("Telegram отключён в config.json — пропускаю.")
        return 0

    try:
        from telethon import TelegramClient
        from telethon.tl.functions.contacts import GetContactsRequest
    except ImportError:
        say("Не установлена библиотека telethon:  python -m pip install -r requirements.txt")
        return 1

    api_id = int(tg.get("api_id") or 0)
    api_hash = tg.get("api_hash") or ""

    sessions = [p.stem for p in sorted(TG_DIR.glob("*.session"))]
    if not sessions:
        say("Нет ни одной сессии Telegram. Сначала выполните вход (шаг 2).")
        return 1

    head("Шаг 3 из 5. Контакты из Telegram")

    async def pull(name):
        client = TelegramClient(str(TG_DIR / name), api_id, api_hash)
        await client.connect()
        try:
            if not await client.is_user_authorized():
                say(f"  {name}: сессия не авторизована, пропускаю.")
                return
            res = await client(GetContactsRequest(hash=0))
            out = []
            for u in res.users:
                if getattr(u, "bot", False):
                    continue
                out.append({
                    "id": u.id,
                    "first_name": u.first_name or "",
                    "last_name": u.last_name or "",
                    "username": u.username or "",
                    "phone": u.phone or "",
                    "bot": False,
                })
            path = TG_DIR / f"contacts_{name}.json"
            path.write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")
            with_phone = sum(1 for x in out if x["phone"])
            with_user = sum(1 for x in out if x["username"])
            say(f"  {name}: {len(out)} контактов (с телефоном {with_phone}, с @ {with_user})")
        finally:
            await client.disconnect()

    async def run():
        for name in sessions:
            try:
                await pull(name)
            except Exception as e:
                say(f"  {name}: ошибка {type(e).__name__}: {str(e)[:160]}")

    asyncio.run(run())
    say("Готово.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
