#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Сторож Доктора: проверки работоспособности систем.

Этап 1 (изолированный прогон): только читает, ничего не чинит, никуда не шлёт.
Запуск:  python3 storozh.py            — отчёт в консоль, код 1 при FAIL
         python3 storozh.py --json     — то же в JSON

Проверки уточнены по фактам прогона 2026-11-25:
- 443 на сервере держит xray, nginx слушает 80 и 8443 → HTTPS проверяем на 8443;
- веб DSH закрыт паролем и отдаёт 401 → 401 считается «жив»;
- ВК с серверного IP не открывается (handshake timeout) → это WARN, а не поломка;
- в журнале много ошибок sshd от SSH-туннеля → их не считаем.
"""
from __future__ import annotations

import argparse
import json
import os
import platform
import shutil
import socket
import ssl
import subprocess
import sys
import time
import urllib.error
import urllib.request
from datetime import datetime, timezone

OK, WARN, FAIL, SKIP = "OK", "WARN", "FAIL", "SKIP"
RESULTS: list[dict] = []
DOMAIN = "2-31-104-44.sslip.io"
HTTPS_PORT = 8443


def _run(cmd: list[str], timeout: int = 15) -> tuple[int, str]:
    try:
        p = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
        return p.returncode, (p.stdout or "") + (p.stderr or "")
    except Exception as e:  # noqa: BLE001
        return 1, str(e)


def add(name: str, status: str, detail: str, fix: str = "") -> None:
    RESULTS.append({"check": name, "status": status, "detail": detail, "autofix": fix})


# ---------------------------------------------------------------- 1. диск
def check_disk(threshold_warn: int = 85, threshold_fail: int = 92) -> None:
    rc, out = _run(["df", "-P", "/"])
    if rc != 0:
        add("диск", FAIL, f"df не сработал: {out[:120]}")
        return
    line = out.strip().splitlines()[-1].split()
    pct = int(line[4].rstrip("%"))
    free_gb = round(int(line[3]) / 1024 / 1024, 1)
    if pct >= threshold_fail:
        add("диск", FAIL, f"занято {pct}% (свободно {free_gb} ГБ)", "чистка логов старше 14 дней")
    elif pct >= threshold_warn:
        add("диск", WARN, f"занято {pct}% (свободно {free_gb} ГБ)", "чистка логов старше 14 дней")
    else:
        add("диск", OK, f"занято {pct}% (свободно {free_gb} ГБ)")


# ---------------------------------------------------------------- 2. память
def check_memory(fail_pct: int = 92) -> None:
    if platform.system() != "Linux":
        add("память", SKIP, "проверка рассчитана на сервер (Linux)")
        return
    try:
        info = {}
        with open("/proc/meminfo") as f:
            for line in f:
                k, v = line.split(":", 1)
                info[k] = int(v.strip().split()[0])
        total, avail = info["MemTotal"], info.get("MemAvailable", 0)
        used_pct = round((total - avail) * 100 / total)
    except Exception as e:  # noqa: BLE001
        add("память", SKIP, f"не прочитать /proc/meminfo: {e}")
        return
    if used_pct >= fail_pct:
        add("память", FAIL, f"занято {used_pct}%")
    elif used_pct >= 80:
        add("память", WARN, f"занято {used_pct}%")
    else:
        add("память", OK, f"занято {used_pct}% (свободно {round(avail/1024)} МБ)")


# ---------------------------------------------------------------- 3. нагрузка
def check_load(max_ratio: float = 2.0) -> None:
    if platform.system() != "Linux":
        add("нагрузка", SKIP, "проверка рассчитана на сервер (Linux)")
        return
    cores = os.cpu_count() or 1
    load1 = os.getloadavg()[0]
    if load1 > cores * max_ratio:
        add("нагрузка", WARN, f"load {load1:.2f} при {cores} ядрах")
    else:
        add("нагрузка", OK, f"load {load1:.2f} при {cores} ядрах")


# ---------------------------------------------------------------- 4. юниты
def check_units(required: list[str]) -> None:
    if platform.system() != "Linux" or not shutil.which("systemctl"):
        add("systemd: юниты", SKIP, "проверка только для сервера на Linux")
        return
    rc, out = _run(["systemctl", "--failed", "--no-legend", "--no-pager"])
    failed = [l.split()[0] for l in out.strip().splitlines() if l.strip()] if rc == 0 else []
    if failed:
        add("systemd: сбойные юниты", FAIL, ", ".join(failed), "systemctl restart <юнит>")
    else:
        add("systemd: сбойные юниты", OK, "нет")

    dead = []
    for unit in required:
        rc, out = _run(["systemctl", "is-active", unit])
        if out.strip() != "active":
            dead.append(f"{unit}={out.strip() or 'нет'}")
    if dead:
        add("systemd: ключевые сервисы", FAIL, ", ".join(dead), "systemctl restart <юнит>")
    else:
        add("systemd: ключевые сервисы", OK, f"{len(required)} активны")


# ---------------------------------------------------------------- 5. HTTP
class _NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):  # noqa: D102
        return None


_OPENER = urllib.request.build_opener(_NoRedirect)


def check_http(name: str, url: str, expect: str = "", alive: tuple[int, ...] = (200,),
               timeout: int = 10, host: str = "", soft: tuple[int, ...] = ()) -> None:
    headers = {"User-Agent": "doktor-storozh/0.1"}
    if host:
        headers["Host"] = host
    req = urllib.request.Request(url, headers=headers)
    started = time.time()
    code, body = 0, ""
    try:
        with _OPENER.open(req, timeout=timeout) as r:
            code, body = r.status, r.read(400_000).decode("utf-8", "ignore")
    except urllib.error.HTTPError as e:
        code = e.code
        try:
            body = e.read(200_000).decode("utf-8", "ignore")
        except Exception:  # noqa: BLE001
            body = ""
    except Exception as e:  # noqa: BLE001
        add(name, FAIL, f"нет ответа: {type(e).__name__} {str(e)[:90]}")
        return
    ms = int((time.time() - started) * 1000)
    if code in soft:
        add(name, WARN, f"HTTP {code} — вероятно капча или редирект, {ms} мс")
    elif code not in alive:
        add(name, FAIL, f"HTTP {code}, {ms} мс")
    elif expect and expect.lower() not in body.lower():
        add(name, WARN, f"{code}, но нет текста «{expect}», {ms} мс")
    else:
        add(name, OK, f"{code}, {ms} мс")


# ---------------------------------------------------------------- 6. git
def check_git(repo: str, max_age_hours: int = 24) -> None:
    if not os.path.isdir(repo):
        add("git: репозиторий", WARN, f"нет папки {repo}")
        return
    if not os.path.isdir(os.path.join(repo, ".git")):
        add("git: репозиторий", WARN, f"папка {repo} без .git (пустой клон)")
        return
    rc, out = _run(["git", "-C", repo, "log", "-1", "--format=%ct"])
    if rc != 0:
        add("git: последний коммит", FAIL, out[:100])
        return
    age_h = (time.time() - int(out.strip())) / 3600
    if age_h > max_age_hours:
        add("git: последний коммит", WARN, f"{age_h:.1f} ч назад (порог {max_age_hours} ч)")
    else:
        add("git: последний коммит", OK, f"{age_h:.1f} ч назад")
    rc, out = _run(["git", "-C", repo, "status", "--porcelain"])
    dirty = len([l for l in out.splitlines() if l.strip()])
    add("git: незакоммиченное", OK if dirty == 0 else WARN, f"{dirty} изменений")


# ---------------------------------------------------------------- 7. сертификат
def check_cert(host: str, port: int = 443, min_days: int = 14) -> None:
    try:
        ctx = ssl.create_default_context()
        with socket.create_connection((host, port), timeout=8) as sock:
            with ctx.wrap_socket(sock, server_hostname=host) as ss:
                cert = ss.getpeercert()
        expires = datetime.strptime(cert["notAfter"], "%b %d %H:%M:%S %Y %Z").replace(tzinfo=timezone.utc)
        days = (expires - datetime.now(timezone.utc)).days
        add("сертификат", FAIL if days < min_days else OK, f"{host}:{port} — {days} дн.", "certbot renew")
    except Exception as e:  # noqa: BLE001
        add("сертификат", FAIL, f"{host}:{port} — {type(e).__name__}: {str(e)[:80]}", "certbot renew")


# ---------------------------------------------------------------- 8. журнал
def check_journal(hours: int = 2, max_errors: int = 5, ignore: str = "sshd") -> None:
    rc, out = _run(["journalctl", "--since", f"-{hours}h", "-p", "err", "--no-pager", "-q"], timeout=20)
    if rc != 0:
        add("журнал: ошибки", SKIP, "journalctl недоступен")
        return
    lines = [l for l in out.splitlines() if l.strip() and ignore not in l]
    if len(lines) > max_errors:
        add("журнал: ошибки", WARN, f"{len(lines)} строк ошибок за {hours} ч (без {ignore})")
    else:
        add("журнал: ошибки", OK, f"{len(lines)} строк за {hours} ч (без {ignore})")


# ---------------------------------------------------------------- 9. не настроено
def check_not_yet() -> None:
    for name, reason in [
        ("пульс Mac-агентов", "этап 5: Mac ещё не отправляет пульс"),
        ("свежесть заявок", "этап 5: нет доступа к журналу заявок с сервера"),
        ("бэкапы", "этап 3: бэкап ещё не настроен на сервере"),
        ("токены ВК/Telegram/MAX/LLM", "этап 2: секреты на сервер пока не ставились"),
    ]:
        add(name, SKIP, reason)


# ---------------------------------------------------------------- отчёт
def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--repo", default="/root/moi-proekty")
    ap.add_argument("--local", action="store_true", help="запуск на Mac: часть проверок пропускается")
    args = ap.parse_args()

    check_disk()
    check_memory()
    check_load()
    check_units(["ssh", "dsh-web"])

    if not args.local:
        check_http("веб DSH (локально)", "http://127.0.0.1:49999/", alive=(200, 401, 403))
        check_http("nginx, порт 80", "http://127.0.0.1:80/", alive=(200, 301, 302), host=DOMAIN)
        check_http("домен HTTPS", f"https://{DOMAIN}:{HTTPS_PORT}/", alive=(200, 401, 403))
        check_cert(DOMAIN, HTTPS_PORT)
        check_journal()

    check_http("карточка Яндекс.Карт",
               "https://yandex.ru/maps/org/silver_song_flowers/138890152139/",
               alive=(200,), soft=(301, 302))
    check_http("Telegram-канал", "https://t.me/s_s_flowers", alive=(200,), soft=(301, 302))
    check_http("ВК-группа (с сервера)", "https://vk.com/s_sflowers", alive=(200,), soft=(301, 302))
    if RESULTS[-1]["status"] == FAIL:
        RESULTS[-1]["status"] = WARN
        RESULTS[-1]["detail"] = "недоступно с серверного IP — проверять с Mac или через прокси"

    check_git(args.repo)
    check_not_yet()

    counts = {s: sum(1 for r in RESULTS if r["status"] == s) for s in (OK, WARN, FAIL, SKIP)}
    if args.json:
        print(json.dumps({"checks": RESULTS, "summary": counts}, ensure_ascii=False, indent=1))
    else:
        print("== Доктор: сторож, этап 1 (только чтение) ==")
        print(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        for r in RESULTS:
            fix = f"  → {r['autofix']}" if r["autofix"] else ""
            print(f"{r['status']:<4} {r['check']}: {r['detail']}{fix}")
        print(f"\nИтог: OK {counts[OK]}, WARN {counts[WARN]}, FAIL {counts[FAIL]}, SKIP {counts[SKIP]}")
    return 1 if counts[FAIL] else 0


if __name__ == "__main__":
    sys.exit(main())
