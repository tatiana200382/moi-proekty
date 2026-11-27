"""Шаг 4. Полные профили: описание, личный канал, ссылки.

Telegram отдаёт описание профиля только по одному запросу на человека,
поэтому шаг идёт со скоростью примерно один профиль в секунду.
Процесс можно прервать и запустить снова — уже собранное не теряется.
"""
import asyncio
import json
import sys

from common import DATA, TG_DIR, head, load_config, say

CONC = 40


def main():
    cfg = load_config()
    tg = cfg["telegram"]
    if not tg.get("enabled", True):
        say("Telegram отключён в config.json — пропускаю.")
        return 0

    try:
        from telethon import TelegramClient
        from telethon.tl.functions.contacts import GetContactsRequest
        from telethon.tl.functions.users import GetFullUserRequest
    except ImportError:
        say("Не установлена библиотека telethon:  python -m pip install -r requirements.txt")
        return 1

    api_id = int(tg.get("api_id") or 0)
    api_hash = tg.get("api_hash") or ""
    sessions = [p.stem for p in sorted(TG_DIR.glob("*.session"))]
    if not sessions:
        say("Нет сессий Telegram. Сначала шаг 2.")
        return 1

    head("Шаг 4 из 5. Профили людей: о себе, каналы, ссылки")

    sem = asyncio.Semaphore(CONC)

    async def one(client, user, acc):
        async with sem:
            for _ in range(4):
                try:
                    full = await client(GetFullUserRequest(user))
                    fu = full.full_user
                    chan = ""
                    pcid = getattr(fu, "personal_channel_id", None)
                    if pcid:
                        for ch in (full.chats or []):
                            if getattr(ch, "id", None) == pcid and getattr(ch, "username", None):
                                chan = f"https://t.me/{ch.username}"
                                break
                    unames = []
                    for u in (getattr(user, "usernames", None) or []):
                        if getattr(u, "active", True) and getattr(u, "username", None):
                            unames.append(u.username)
                    if user.username and user.username not in unames:
                        unames.insert(0, user.username)
                    return {"id": user.id, "acc": acc, "username": user.username or "",
                            "usernames": unames, "phone": user.phone or "",
                            "about": (fu.about or "").strip(), "channel": chan,
                            "channel_title": ""}
                except Exception as e:
                    if type(e).__name__ == "FloodWaitError":
                        await asyncio.sleep(min(getattr(e, "seconds", 5), 15) + 1)
                        continue
                    return None
            return None

    async def run_acc(acc):
        out_path = TG_DIR / f"profiles_{acc}.json"
        have = {}
        if out_path.exists():
            try:
                have = json.loads(out_path.read_text(encoding="utf-8"))
            except Exception:
                have = {}
        client = TelegramClient(str(TG_DIR / acc), api_id, api_hash)
        await client.connect()
        try:
            if not await client.is_user_authorized():
                say(f"  {acc}: сессия не авторизована, пропускаю.")
                return
            res = await client(GetContactsRequest(hash=0))
            todo = [u for u in res.users if f"{acc}:{u.id}" not in have]
            say(f"  {acc}: всего {len(res.users)}, осталось собрать {len(todo)}")
            tasks = [asyncio.create_task(one(client, u, acc)) for u in todo]
            done = 0
            for fut in asyncio.as_completed(tasks):
                r = await fut
                done += 1
                if r:
                    have[f"{acc}:{r['id']}"] = r
                if done % 100 == 0:
                    out_path.write_text(json.dumps(have, ensure_ascii=False, indent=1), encoding="utf-8")
                    say(f"    {done}/{len(todo)}")
            out_path.write_text(json.dumps(have, ensure_ascii=False, indent=1), encoding="utf-8")
            say(f"  {acc}: готово, профилей {len(have)}")
        finally:
            await client.disconnect()

    async def run():
        for acc in sessions:
            try:
                await run_acc(acc)
            except Exception as e:
                say(f"  {acc}: ошибка {type(e).__name__}: {str(e)[:160]}")

    asyncio.run(run())
    say("Готово.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
