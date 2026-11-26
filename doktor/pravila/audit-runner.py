#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Ежедневный аудит правил на сервере.

1. Обновляет копию репозитория (только чтение, публичный HTTPS).
2. Запускает doktor/pravila/audit.py.
3. Есть нарушения — тревога в Telegram с перечнем; нет — тихая запись в журнал.
4. Не смог обновить или запустить — тревога «аудит не выполнен».

Запуск: python3 /opt/doktor/audit-runner.py [--test-alert]
"""
from __future__ import annotations

import json
import subprocess
import sys
import time
from datetime import datetime, timezone

sys.path.insert(0, "/opt/doktor")
from storozh import send_telegram  # noqa: E402

REPO = "/opt/doktor/repo"
STATE = "/var/lib/doktor-audit"
LOG = f"{STATE}/audit.log"
URL = "https://github.com/tatiana200382/moi-proekty.git"


def log(text: str) -> None:
    import os
    os.makedirs(STATE, exist_ok=True)
    with open(LOG, "a", encoding="utf-8") as f:
        f.write(f"{datetime.now(timezone.utc).isoformat(timespec='seconds')} {text}\n")


def sh(cmd: list[str], timeout: int = 120) -> tuple[int, str]:
    p = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
    return p.returncode, (p.stdout or "") + (p.stderr or "")


def main() -> int:
    if "--test-alert" in sys.argv:
        ok, info = send_telegram("🧪 Аудит правил: проверка связи. Тревоги работают.")
        print(("OK: " if ok else "FAIL: ") + info)
        return 0 if ok else 1

    import os
    os.makedirs(STATE, exist_ok=True)
    no_pull = "--no-pull" in sys.argv

    if not no_pull and not os.path.isdir(f"{REPO}/.git"):
        rc, out = sh(["git", "clone", "--depth", "1", URL, REPO], timeout=300)
        log(f"clone rc={rc}")
        if rc != 0:
            send_telegram("🔴 Аудит правил не выполнен: не удалось склонировать репозиторий.\n" + out[-300:])
            return 1

    if no_pull:
        log("прогон без обновления копии (тест)")
    else:
        rc, out = sh(["git", "-C", REPO, "fetch", "--depth", "1", "origin", "main"], timeout=300)
        if rc == 0:
            sh(["git", "-C", REPO, "reset", "--hard", "origin/main"])
        else:
            log(f"fetch rc={rc}: {out[-200:]}")
            send_telegram("🟠 Аудит правил: не удалось обновить копию репозитория, проверяю вчерашнюю.\n" + out[-200:])

    rc, out = sh(["python3", f"{REPO}/doktor/pravila/audit.py", "--json"], timeout=180)
    try:
        data = json.loads(out)
        fails = [c for c in data["checks"] if c["status"] == "FAIL"]
    except Exception:  # noqa: BLE001
        log(f"audit rc={rc} parse error: {out[-300:]}")
        send_telegram("🔴 Аудит правил не выполнен: ошибка запуска.\n" + out[-300:])
        return 1

    log(f"audit rc={rc} fails={len(fails)}")
    if fails:
        lines = ["🔴 Аудит правил: нарушения"]
        lines += [f"• {f['rule']}: {f['detail']}" for f in fails[:8]]
        lines.append("Разбор — в журнале нарушений и отчёте Доктора.")
        ok, info = send_telegram("\n".join(lines))
        log(f"alert ok={ok} {info}")
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
