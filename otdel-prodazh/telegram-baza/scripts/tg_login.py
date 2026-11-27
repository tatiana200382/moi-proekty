"""Шаг 2. Вход в Telegram и сохранение сессии.

Первый запуск: телефон, код из Telegram, пароль двухфакторной защиты (если включён).
Повторный запуск: вход уже сохранён в файле сессии, код не нужен.
"""
import sys

from common import TG_DIR, head, load_config, save_config, say

def main():
    cfg = load_config()
    tg = cfg["telegram"]
    if not tg.get("enabled", True):
        say("Telegram отключён в config.json — пропускаю.")
        return 0

    head("Шаг 2 из 5. Вход в Telegram")
    try:
        from telethon.sync import TelegramClient
    except ImportError:
        say("Не установлена библиотека telethon.")
        say("Выполните:  python -m pip install -r requirements.txt")
        return 1

    api_id = int(tg.get("api_id") or 0)
    api_hash = tg.get("api_hash") or ""
    if not api_id or not api_hash:
        say("В config.json не заполнены telegram.api_id и telegram.api_hash.")
        say("Возьмите их на my.telegram.org → API development tools.")
        return 1

    sessions = tg.get("sessions") or ["main"]
    if isinstance(sessions, str):
        sessions = [sessions]

    todo = []
    for name in sessions:
        path = str(TG_DIR / name)
        client = TelegramClient(path, api_id, api_hash)
        try:
            client.connect()
            if client.is_user_authorized():
                me = client.get_me()
                say(f"  {name}: уже выполнен вход — {me.first_name or ''} {me.last_name or ''} @{me.username or ''}".rstrip())
                continue
        except Exception as e:
            say(f"  {name}: проверка сессии не удалась ({type(e).__name__})")
        finally:
            try:
                client.disconnect()
            except Exception:
                pass
        todo.append(name)

    if not todo:
        say("Все сессии уже активны — вход не требуется.")
        return 0

    for name in todo:
        say("")
        say(f"Вход в аккаунт «{name}».")
        say("Номер в формате +79991234567. Код придёт в приложение Telegram,")
        say("пароль нужен только если включена двухфакторная защита.")
        phone = input("Номер телефона: ").strip()
        if not phone:
            say("Номер не введён — пропускаю этот аккаунт.")
            continue
        if not phone.startswith("+"):
            phone = "+" + phone.lstrip("+")

        client = TelegramClient(str(TG_DIR / name), api_id, api_hash)
        try:
            client.start(phone=phone)
            me = client.get_me()
            say(f"  Готово: {me.first_name or ''} {me.last_name or ''} @{me.username or ''} (id {me.id})".rstrip())
        except Exception as e:
            say(f"  Не удалось войти: {type(e).__name__}: {str(e)[:200]}")
            say("  Повторите запуск — сессия не сохранена.")
            return 1
        finally:
            try:
                client.disconnect()
            except Exception:
                pass

    if not cfg.get("owner_name"):
        try:
            client = TelegramClient(str(TG_DIR / sessions[0]), api_id, api_hash)
            client.connect()
            me = client.get_me()
            if me:
                cfg["owner_name"] = (me.first_name or "") + " " + (me.last_name or "")
                cfg["owner_name"] = cfg["owner_name"].strip()
                save_config(cfg)
            client.disconnect()
        except Exception:
            pass
    return 0


if __name__ == "__main__":
    sys.exit(main())
