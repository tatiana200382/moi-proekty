#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Сторож Доктора: проверки + автономное лечение по белому списку.

Режимы:
  без флагов            — только проверки (ручной прогон, безопасно)
  --fix                 — проверки + лечение по белому списку (так работает таймер)
  --no-alert            — не отправлять тревоги (тесты)
  --alert-test          — отправить тестовую тревогу и выйти

Правило владельца (2026-11-25): лечить простое — без спроса, но по правилам:
  план в коде → изолированная проверка → откат записан → проверка результата → запись в журнал.
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
import urllib.parse
import urllib.request
from datetime import datetime, timezone

OK, WARN, FAIL, SKIP = "OK", "WARN", "FAIL", "SKIP"
RESULTS: list[dict] = []
DOMAIN = "2-31-104-44.sslip.io"
HTTPS_PORT = 8443

ENV_FILE = "/etc/doktor/env"
STATE_FILE = "/var/lib/doktor/state.json"
ACTION_LOG = "/var/lib/doktor/actions.log"
PAUSE_FILE = "/etc/doktor/PAUSE"
COOLDOWN_H = 6

# Белый список лечения: только это чиним сами.
ALLOWED_UNITS = {"dsh-web", "nginx"}
ALLOWED_PREFIX = "doktor-"
MAX_ACTIONS_PER_HOUR = 3
DISK_FAIL_PCT = 92


def reset() -> None:
    RESULTS.clear()


def _run(cmd: list[str], timeout: int = 15) -> tuple[int, str]:
    try:
        p = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
        return p.returncode, (p.stdout or "") + (p.stderr or "")
    except Exception as e:  # noqa: BLE001
        return 1, str(e)


def add(name: str, status: str, detail: str, fix: str = "") -> None:
    RESULTS.append({"check": name, "status": status, "detail": detail, "autofix": fix})


# ------------------------------------------------------- тревоги в Telegram
def load_env() -> dict:
    env = {}
    try:
        with open(ENV_FILE) as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    k, v = line.split("=", 1)
                    env[k.strip()] = v.strip()
    except FileNotFoundError:
        pass
    return env


def send_telegram(text: str) -> tuple[bool, str]:
    env = load_env()
    token, chat = env.get("TG_TOKEN"), env.get("TG_CHAT")
    if not token or not chat:
        return False, "нет TG_TOKEN/TG_CHAT в /etc/doktor/env"
    data = urllib.parse.urlencode({"chat_id": chat, "text": text[:3900],
                                   "disable_web_page_preview": "true"}).encode()
    try:
        with urllib.request.urlopen(f"https://api.telegram.org/bot{token}/sendMessage",
                                    data=data, timeout=15) as r:
            ok = b'"ok":true' in r.read()
        return ok, "отправлено" if ok else "Telegram ответил ok=false"
    except Exception as e:  # noqa: BLE001
        return False, f"{type(e).__name__}: {str(e)[:120]}"


def _read_json(path: str) -> dict:
    try:
        with open(path) as f:
            return json.load(f)
    except Exception:  # noqa: BLE001
        return {}


def _write_json(path: str, data: dict) -> None:
    try:
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w") as f:
            json.dump(data, f, ensure_ascii=False)
    except Exception:  # noqa: BLE001
        pass


def maybe_alert(counts: dict, fixed: list[dict], quiet: bool = False) -> None:
    fails = [r for r in RESULTS if r["status"] == FAIL]
    state = _read_json(STATE_FILE)
    now = time.time()
    fingerprint = "|".join(sorted(r["check"] for r in fails))

    if fails and not quiet:
        last = float(state.get("last_sent", 0))
        if fingerprint != state.get("fingerprint") or now - last > COOLDOWN_H * 3600:
            lines = [f"🔴 Доктор: {len(fails)} поломк(и)"]
            lines += [f"• {r['check']}: {r['detail']}" for r in fails]
            if fixed:
                lines.append("Пытался починить:")
                lines += [f"→ {f['check']}: {'ok' if f['ok'] else 'не вышло'} — {f['msg']}" for f in fixed]
            ok, info = send_telegram("\n".join(lines))
            if ok:
                state.update(fingerprint=fingerprint, last_sent=now, status="fail")
            else:
                print(f"тревога не ушла: {info}", file=sys.stderr)
    elif fails:
        state.update(fingerprint=fingerprint, status="fail")
    elif state.get("status") == "fail" and not quiet:
        text = "🟢 Доктор: восстановлено, поломок нет."
        if fixed:
            text += "\nПочинил сам: " + "; ".join(f"{f['check']} — {f['msg']}" for f in fixed if f["ok"])
        ok, _info = send_telegram(text)
        if ok:
            state.update(status="ok", fingerprint="", last_sent=now)
    else:
        state.update(status="ok", fingerprint="")

    _write_json(STATE_FILE, state)


# ------------------------------------------------------- журнал действий
def log_action(entry: dict) -> None:
    entry["ts"] = datetime.now(timezone.utc).isoformat(timespec="seconds")
    try:
        os.makedirs(os.path.dirname(ACTION_LOG), exist_ok=True)
        with open(ACTION_LOG, "a") as f:
            f.write(json.dumps(entry, ensure_ascii=False) + "\n")
    except Exception:  # noqa: BLE001
        pass


def actions_last_hour() -> int:
    try:
        cutoff = time.time() - 3600
        n = 0
        with open(ACTION_LOG) as f:
            for line in f:
                try:
                    if datetime.fromisoformat(json.loads(line)["ts"]).timestamp() > cutoff:
                        n += 1
                except Exception:  # noqa: BLE001
                    continue
        return n
    except FileNotFoundError:
        return 0


# ---------------------------------------------------------------- 1. диск
DISK_PCT = 0


def check_disk(threshold_warn: int = 85, threshold_fail: int = DISK_FAIL_PCT) -> None:
    global DISK_PCT
    rc, out = _run(["df", "-P", "/"])
    if rc != 0:
        add("диск", FAIL, f"df не сработал: {out[:120]}")
        return
    line = out.strip().splitlines()[-1].split()
    pct = int(line[4].rstrip("%"))
    DISK_PCT = pct
    free_gb = round(int(line[3]) / 1024 / 1024, 1)
    if pct >= threshold_fail:
        add("диск", FAIL, f"занято {pct}% (свободно {free_gb} ГБ)", "vacuum журнала старше 14 дней")
    elif pct >= threshold_warn:
        add("диск", WARN, f"занято {pct}% (свободно {free_gb} ГБ)", "vacuum журнала старше 14 дней")
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
    headers = {"User-Agent": "doktor-storozh/0.2"}
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


# ---------------------------------------------------------------- лечение
def _unit_allowed(unit: str) -> bool:
    return unit in ALLOWED_UNITS or unit.startswith(ALLOWED_PREFIX)


def fix_units(check: dict) -> list[dict]:
    fixed = []
    text = check["detail"]
    if "=" in text:
        units = [p.split("=")[0].strip() for p in text.split(",") if "=" in p]
    else:
        units = [u.strip() for u in text.split(",") if u.strip()]
    for unit in units:
        if not _unit_allowed(unit):
            fixed.append({"check": unit, "ok": False, "msg": "не в белом списке — сообщаю, не трогаю"})
            continue
        rc, out = _run(["systemctl", "restart", unit], timeout=60)
        time.sleep(2)
        active = _run(["systemctl", "is-active", unit])[1].strip() == "active"
        log_action({"action": "restart", "unit": unit, "rc": rc, "active": active,
                    "rollback": f"systemctl stop {unit}"})
        fixed.append({"check": unit, "ok": active,
                      "msg": "перезапущен и работает" if active else f"перезапуск не помог: {out[:80]}"})
    return fixed


def fix_disk(check: dict) -> list[dict]:
    before = check["detail"]
    _run(["journalctl", "--vacuum-time=14d"], timeout=120)
    rc, out = _run(["df", "-P", "/"])
    log_action({"action": "journal_vacuum", "unit": "", "rc": rc,
                "rollback": "нет: удалены только записи журнала старше 14 дней"})
    after = out.strip().splitlines()[-1].split()[4] if out.strip() else "?"
    return [{"check": "диск", "ok": True, "msg": f"журнал почищен: было {before}, стало занято {after}"}]


def fix_cert(check: dict) -> list[dict]:
    rc, out = _run(["certbot", "renew", "--quiet"], timeout=180)
    ok = rc == 0
    log_action({"action": "certbot_renew", "unit": "", "rc": rc, "rollback": "certbot не меняет старый сертификат до успеха"})
    return [{"check": "сертификат", "ok": ok, "msg": "сертификат обновлён" if ok else f"certbot: {out[:100]}"}]


def apply_fixes(fails: list[dict]) -> list[dict]:
    """Лечим только то, что в белом списке; остальное — в тревогу."""
    fixed: list[dict] = []
    if os.path.exists(PAUSE_FILE):
        log_action({"action": "paused", "unit": "", "rollback": f"rm {PAUSE_FILE}"})
        return [{"check": "все", "ok": False, "msg": "лечение на паузе (/etc/doktor/PAUSE)"}]

    for check in fails:
        name, detail = check["check"], check["detail"]
        if actions_last_hour() >= MAX_ACTIONS_PER_HOUR:
            fixed.append({"check": name, "ok": False,
                          "msg": f"лимит {MAX_ACTIONS_PER_HOUR} действий в час — жду человека"})
            break
        if name.startswith("systemd: "):
            fixed += fix_units(check)
        elif name == "диск" and DISK_PCT >= DISK_FAIL_PCT:
            fixed += fix_disk(check)
        elif name == "сертификат":
            fixed += fix_cert(check)
        else:
            fixed.append({"check": name, "ok": False, "msg": "нет рецепта — нужно решение человека"})
    return fixed


# ---------------------------------------------------------------- прогон
def run_all(args) -> dict:
    reset()
    check_disk()
    check_memory()
    check_load()
    check_units([u.strip() for u in args.units.split(",") if u.strip()])

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
    before = len(RESULTS)
    check_http("ВК-группа (с сервера)", "https://vk.com/s_sflowers", alive=(200,), soft=(301, 302))
    if len(RESULTS) > before and RESULTS[-1]["status"] == FAIL:
        RESULTS[-1]["status"] = WARN
        RESULTS[-1]["detail"] = "недоступно с серверного IP — проверять с Mac или через прокси"

    check_git(args.repo)
    check_not_yet()
    return {s: sum(1 for r in RESULTS if r["status"] == s) for s in (OK, WARN, FAIL, SKIP)}


def print_report(counts: dict, title: str) -> None:
    print(f"== {title} ==")
    print(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    for r in RESULTS:
        fix = f"  → {r['autofix']}" if r["autofix"] else ""
        print(f"{r['status']:<4} {r['check']}: {r['detail']}{fix}")
    print(f"\nИтог: OK {counts[OK]}, WARN {counts[WARN]}, FAIL {counts[FAIL]}, SKIP {counts[SKIP]}")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--repo", default="/root/moi-proekty")
    ap.add_argument("--local", action="store_true", help="запуск на Mac: часть проверок пропускается")
    ap.add_argument("--no-alert", action="store_true", help="не отправлять тревоги")
    ap.add_argument("--no-fix", action="store_true", help="не лечить, только проверять")
    ap.add_argument("--fix", action="store_true", help="лечить по белому списку (так работает таймер)")
    ap.add_argument("--alert-test", action="store_true", help="отправить тестовую тревогу и выйти")
    ap.add_argument("--units", default=os.environ.get("DOKTOR_UNITS", "ssh,dsh-web"))
    args = ap.parse_args()

    if args.alert_test:
        ok, info = send_telegram("🧪 Доктор: проверка связи. Если вы это видите — тревоги работают.")
        print(("OK: " if ok else "FAIL: ") + info)
        return 0 if ok else 1

    counts = run_all(args)
    fixed: list[dict] = []

    if counts[FAIL] and args.fix and not args.no_fix and not args.local:
        fixed = apply_fixes([r for r in RESULTS if r["status"] == FAIL])
        if any(f["ok"] for f in fixed):
            counts = run_all(args)  # проверяем результат лечения

    maybe_alert(counts, fixed, quiet=args.no_alert or args.local)

    if args.json:
        print(json.dumps({"checks": RESULTS, "summary": counts, "fixed": fixed}, ensure_ascii=False, indent=1))
    else:
        print_report(counts, "Доктор: сторож + лечение" if not args.no_fix else "Доктор: сторож (только чтение)")
        if fixed:
            print("\nЛечение:")
            for f in fixed:
                print(f"  {'ok' if f['ok'] else 'нет'} {f['check']}: {f['msg']}")
    return 1 if counts[FAIL] else 0


if __name__ == "__main__":
    sys.exit(main())
