"""Шаг 4б. Люди из рабочих чатов.

Для каждого чата из config.json → telegram.chats:
  * участники группы;
  * все упоминания @username и ссылки t.me в переписке;
  * фраза, в которой человек упомянут (чтобы понять, зачем он в базе).
"""
import asyncio
import json
import re
import sys

from common import TG_DIR, head, load_config, say

MSG_LIMIT = 5000
HANDLE_RE = re.compile(r"@([A-Za-z0-9_]{4,32})")
LINK_RE = re.compile(r"t\.me/([A-Za-z0-9_]{4,32})")


def snippet_for(text, handle):
    m = re.search(r"[@/]" + re.escape(handle) + r"\b", text, re.I)
    if not m:
        return text[:160].replace("\n", " ")
    a = max(0, m.start() - 110)
    b = min(len(text), m.end() + 130)
    return text[a:b].replace("\n", " ").strip()


def main():
    cfg = load_config()
    tg = cfg["telegram"]
    chats = tg.get("chats") or []
    if not chats:
        say("В config.json не указаны чаты (telegram.chats) — шаг пропущен.")
        return 0

    try:
        from telethon import TelegramClient
        from telethon.tl.functions.channels import GetParticipantsRequest
        from telethon.tl.functions.users import GetFullUserRequest
        from telethon.tl.types import ChannelParticipantsSearch
    except ImportError:
        say("Не установлена библиотека telethon:  python -m pip install -r requirements.txt")
        return 1

    api_id = int(tg.get("api_id") or 0)
    api_hash = tg.get("api_hash") or ""
    sessions = [p.stem for p in sorted(TG_DIR.glob("*.session"))]
    if not sessions:
        say("Нет сессий Telegram. Сначала шаг 2.")
        return 1

    head("Шаг 4б. Люди из рабочих чатов")

    async def harvest(client, title):
        found = None
        async for d in client.iter_dialogs():
            if (d.title or "").strip().lower() == title.strip().lower():
                found = d.entity
                break
        if found is None:
            say(f"  «{title}»: чат не найден среди диалогов — пропускаю.")
            return []

        handles, best = set(), {}
        try:
            if hasattr(found, "megagroup") or hasattr(found, "broadcast"):
                res = await client(GetParticipantsRequest(channel=found, filter=ChannelParticipantsSearch(""),
                                                          offset=0, limit=200, hash=0))
                for u in res.users:
                    if getattr(u, "username", None):
                        handles.add(u.username)
        except Exception as e:
            say(f"  «{title}»: участников получить не удалось ({type(e).__name__})")

        count = 0
        async for m in client.iter_messages(found, limit=MSG_LIMIT):
            t = (m.message or "").strip()
            if not t:
                continue
            count += 1
            for h in set(HANDLE_RE.findall(t)) | set(LINK_RE.findall(t)):
                handles.add(h)
                s = snippet_for(t, h)
                if h not in best or len(s) < len(best[h]):
                    best[h] = s

        say(f"  «{title}»: сообщений {count}, упоминаний {len(handles)}")

        out = []
        for h in sorted(handles):
            try:
                e = await client.get_entity(h)
            except Exception:
                out.append({"handle": h, "kind": "unresolved", "snippet": best.get(h, ""), "chat": title})
                continue
            rec = {"handle": h, "kind": type(e).__name__, "id": e.id,
                   "username": getattr(e, "username", "") or "",
                   "first_name": getattr(e, "first_name", "") or "",
                   "last_name": getattr(e, "last_name", "") or "",
                   "title": getattr(e, "title", "") or "",
                   "bot": bool(getattr(e, "bot", False)),
                   "phone": getattr(e, "phone", "") or "",
                   "snippet": best.get(h, ""), "chat": title}
            if rec["kind"] == "User" and not rec["bot"]:
                try:
                    full = await client(GetFullUserRequest(e))
                    rec["about"] = (full.full_user.about or "").strip()
                    pcid = getattr(full.full_user, "personal_channel_id", None)
                    if pcid:
                        for ch in (full.chats or []):
                            if getattr(ch, "id", None) == pcid and getattr(ch, "username", None):
                                rec["channel"] = f"https://t.me/{ch.username}"
                                break
                except Exception:
                    pass
            out.append(rec)
        return out

    async def run():
        acc = sessions[0]
        client = TelegramClient(str(TG_DIR / acc), api_id, api_hash)
        await client.connect()
        try:
            if not await client.is_user_authorized():
                say(f"  {acc}: сессия не авторизована.")
                return
            refs = []
            for title in chats:
                try:
                    refs += await harvest(client, title)
                except Exception as e:
                    say(f"  «{title}»: ошибка {type(e).__name__}: {str(e)[:160]}")
            path = TG_DIR / "chat_refs.json"
            path.write_text(json.dumps(refs, ensure_ascii=False, indent=1), encoding="utf-8")
            bots = sum(1 for r in refs if r.get("bot"))
            say(f"  сохранено {len(refs)} упоминаний (ботов {bots}); из них новых для базы определит следующий шаг")
        finally:
            await client.disconnect()

    asyncio.run(run())
    say("Готово.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
