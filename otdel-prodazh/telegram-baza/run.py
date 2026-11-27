"""Один запуск — вся сборка базы контактов.

Порядок шагов:
  1. контакты с телефона (ADB)
  2. вход в Telegram
  3. контакт-листы из Telegram
  4. профили: о себе, каналы, ссылки
  4б. люди из рабочих чатов (если указаны в config.json)
  5. склейка, классификация, Excel

Запуск:  Собрать-базу.cmd   (или python run.py)
"""
import subprocess
import sys
import time

from common import OUTPUT, ROOT, SCRIPTS, head, load_config, say

STEPS = [
    ("phone_pull.py", "Контакты с телефона", True),
    ("phone_parse.py", "Разбор телефонной книги", True),
    ("tg_login.py", "Вход в Telegram", False),
    ("tg_contacts.py", "Контакты из Telegram", False),
    ("tg_profiles.py", "Профили: о себе и ссылки", False),
    ("tg_chat.py", "Люди из рабочих чатов", False),
    ("merge.py", "Склейка источников", False),
    ("build_db.py", "Классификация", False),
    ("report.py", "Сборка Excel", False),
]


def run_step(script, title, optional):
    head(title)
    started = time.time()
    res = subprocess.run([sys.executable, str(SCRIPTS / script), *EXTRA.get(script, [])],
                         cwd=str(SCRIPTS))
    took = time.time() - started
    if res.returncode != 0:
        if optional:
            say(f"  Шаг пропущен (код {res.returncode}). Продолжаю.")
            return True
        say(f"  Шаг не удался (код {res.returncode}).")
        return False
    say(f"  Готово за {took:.0f} с")
    return True


EXTRA = {}


def main():
    args = sys.argv[1:]
    global EXTRA
    skip = {a for a in args if a.startswith("--skip-")}
    only = [a for a in args if a.startswith("--only=")]

    cfg = load_config()
    say("")
    say("  Сбор базы контактов")
    say("  телефон + Telegram → размеченная база в Excel")
    say("")
    say(f"  Папка:   {ROOT}")
    say(f"  Телефон: {'включён' if cfg['phone'].get('enabled', True) else 'выключен'}")
    say(f"  Telegram: {'включён' if cfg['telegram'].get('enabled', True) else 'выключен'}")
    chats = cfg["telegram"].get("chats") or []
    say(f"  Чаты:    {', '.join(chats) if chats else 'не указаны'}")

    if "--skip-phone" in skip:
        cfg["phone"]["enabled"] = False
        say("  (телефон пропущен по флагу)")
    if "--skip-telegram" in skip:
        cfg["telegram"]["enabled"] = False

    for script, title, optional in STEPS:
        if only and not any(script.startswith(o.split("=")[1]) for o in only):
            continue
        if script.startswith("phone_") and not cfg["phone"].get("enabled", True):
            say(f"—— {title}: выключено в настройках, пропускаю")
            continue
        if script.startswith("tg_") and not cfg["telegram"].get("enabled", True):
            say(f"—— {title}: Telegram выключен, пропускаю")
            continue
        if not run_step(script, title, optional):
            say("")
            say("Сборка остановлена. Исправьте ошибку выше и запустите снова —")
            say("уже сделанные шаги повторять не нужно, данные сохранены.")
            return 1

    files = sorted(OUTPUT.glob("*.xlsx"))
    head("Готово")
    if files:
        for f in files:
            say(f"  Файл: {f}")
    else:
        say("  Excel не создан — проверьте сообщения выше.")
    say("")
    say("  Откройте файл и посмотрите листы «Сводка», «Подрядчики», «База».")
    return 0


if __name__ == "__main__":
    sys.exit(main())
