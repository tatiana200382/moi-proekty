"""Шаг 1. Выгрузка контактов с телефона через ADB.

Телефон подключён по USB, включена отладка, на экране подтверждён доступ.
Скрипт снимает четыре таблицы контактов Android и складывает их в data/phone/.
"""
import subprocess
import sys

from common import PHONE_DIR, head, load_config, say

TABLES = {
    "raw_contacts.txt": "content://com.android.contacts/raw_contacts",
    "data.txt": "content://com.android.contacts/data",
    "contacts.txt": "content://com.android.contacts/contacts",
    "groups.txt": "content://com.android.contacts/groups",
}


def adb(path, *args, timeout=180):
    return subprocess.run([path, *args], capture_output=True, text=True,
                          encoding="utf-8", errors="replace", timeout=timeout)


def main():
    cfg = load_config()
    if not cfg["phone"].get("enabled", True):
        say("Выгрузка с телефона отключена в config.json — пропускаю.")
        return 0

    adb_path = cfg["phone"].get("adb_path") or "adb"
    head("Шаг 1 из 5. Контакты с телефона")

    try:
        devices = adb(adb_path, "devices", timeout=60)
    except FileNotFoundError:
        say(f"ADB не найден по пути «{adb_path}».")
        say("Установите platform-tools и укажите полный путь к adb.exe в config.json:")
        say('  "phone": { "adb_path": "C:\\\\platform-tools\\\\adb.exe" }')
        return 1
    except subprocess.TimeoutExpired:
        say("ADB не ответил за минуту. Переподключите кабель и запустите снова.")
        return 1

    if devices.returncode != 0:
        say(devices.stderr.strip()[:400])
        return 1

    lines = [l for l in devices.stdout.splitlines() if l.strip()]
    connected = [l for l in lines[1:] if "\tdevice" in l]
    if not connected:
        say("Телефон не найден. Проверьте:")
        say("  1) кабель подключён и режим «Передача файлов»;")
        say("  2) в настройках разработчика включена «Отладка по USB»;")
        say("  3) на экране телефона подтверждён запрос «Разрешить отладку».")
        say("")
        say("Ответ adb: " + (lines[1] if len(lines) > 1 else "пусто"))
        return 1

    say(f"Устройство: {connected[0].split(chr(9))[0]}")

    ok = 0
    for name, uri in TABLES.items():
        res = adb(adb_path, "shell", "content", "query", "--uri", uri)
        out = res.stdout or ""
        if res.returncode != 0 or not out.strip():
            say(f"  {name}: нет данных ({res.stderr.strip()[:120]})")
            continue
        (PHONE_DIR / name).write_text(out, encoding="utf-8")
        rows = sum(1 for l in out.splitlines() if l.startswith("Row:"))
        say(f"  {name}: {rows} строк")
        ok += 1

    if ok == 0:
        say("Ни одной таблицы получить не удалось. Скорее всего, не подтверждён доступ на экране телефона.")
        return 1

    say("Готово.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
