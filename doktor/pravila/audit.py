#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Аудит правил: ищет обходы и нарушения.

Только читает. Ничего не удаляет и не правит — показывает факты.
Код выхода: 0 — нарушений нет, 1 — есть FAIL.

Использование: python3 doktor/pravila/audit.py [--json]
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import subprocess
import sys
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PRAVILA_DIR = ROOT / "doktor" / "pravila"
BASELINE = PRAVILA_DIR / ".hashes"
ZHURNAL_PRAVIL = PRAVILA_DIR / "zhurnal-pravil.md"
NARUSHENIYA = ROOT / "doktor" / "narusheniya.md"
STOP = PRAVILA_DIR / "STOP"
VAULT = Path.home() / "AI-Memory-Lab" / "01_проекты"

ROOT_ALLOWED = {
    "AGENTS.md", "CLAUDE.md", "PRAVILA.md", "PRAVILA-ANTI-BAN.md", "STRUKTURA.md",
    "komanda.md", "shablon-agenta.md", "uroki.md", "profil-ai.md", "profil-ai-perenosimyy.md",
    "plan-testov.md", "Журнал.md", "Идеи.md", "Напоминания.md", "hello.md", "summary.md",
    "github.md", "pravila-dlya-gpt.md", "nastroyka-bota.md", "gpt-vhod.md", "avito-review.md",
    "vybor-instrumentov.md", "skazat.sh", "AGENTS.md.bak-20261126",
}

SECRET_PATTERNS = [
    ("токен Telegram", re.compile(r"\b\d{8,10}:[A-Za-z0-9_-]{30,}\b")),
    ("ключ OpenAI/DeepSeek", re.compile(r"\bsk-[A-Za-z0-9]{20,}\b")),
    ("приватный ключ", re.compile(r"BEGIN [A-Z ]*PRIVATE KEY")),
    ("пароль в файле", re.compile(r"(?i)(password|passwd|pwd)\s*=\s*['\"]?[^\s'\"]{6,}")),
    ("api-ключ", re.compile(r"(?i)(api[_-]?key|token)\s*[:=]\s*['\"][A-Za-z0-9_\-]{20,}")),
]

RESULTS: list[dict] = []


def add(rule: str, status: str, detail: str) -> None:
    RESULTS.append({"rule": rule, "status": status, "detail": detail})


def git(*args: str) -> str:
    p = subprocess.run(["git", "-C", str(ROOT), *args], capture_output=True, text=True)
    return p.stdout


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()[:16]


# ---------------------------------------------------------------- проверки
def check_secrets() -> None:
    files = [f for f in git("ls-files").splitlines() if f.strip()]
    text_ext = {".md", ".py", ".sh", ".mjs", ".json", ".yaml", ".yml", ".txt", ".csv", ".toml"}
    found = []
    for rel in files:
        p = ROOT / rel
        if p.suffix.lower() not in text_ext or not p.is_file() or p.stat().st_size > 2_000_000:
            continue
        try:
            body = p.read_text("utf-8", "ignore")
        except Exception:  # noqa: BLE001
            continue
        for name, rx in SECRET_PATTERNS:
            if rx.search(body):
                found.append(f"{rel} — {name}")
    if found:
        add("П4 секреты", "FAIL", "найдено: " + "; ".join(found[:5]))
    else:
        add("П4 секреты", "OK", f"проверено файлов: {len(files)}")


def check_rules_changed() -> None:
    if not ZHURNAL_PRAVIL.exists():
        ZHURNAL_PRAVIL.write_text(
            "# Журнал правок правил\n\nОдна строка — одна правка: дата, что изменили, "
            "разрешение владельца, хеш `PRAVILA.md` после правки.\n\n"
            "| Дата | Что изменили | Разрешение | Хеш |\n|---|---|---|---|\n",
            "utf-8",
        )
    current = sha(ROOT / "PRAVILA.md")
    if not BASELINE.exists():
        BASELINE.write_text(json.dumps({"PRAVILA.md": current}, ensure_ascii=False), "utf-8")
        add("П5 правила без записи", "SKIP", f"базовая линия записана: {current}")
        return
    base = json.loads(BASELINE.read_text("utf-8")).get("PRAVILA.md", "")
    if current == base:
        add("П5 правила без записи", "OK", f"хеш не менялся: {current}")
        return
    journal = ZHURNAL_PRAVIL.read_text("utf-8")
    if current in journal:
        add("П5 правила без записи", "OK", f"правка записана: {current}")
    else:
        add("П5 правила без записи", "FAIL",
            f"PRAVILA.md изменён ({base} → {current}), записи в журнале правок нет")


def check_plans() -> None:
    plans = sorted((ROOT / "plany").glob("*.md"))
    bad = []
    for p in plans:
        body = p.read_text("utf-8", "ignore")
        if p.name == "shablon.md":
            continue
        missing = []
        if "Откат" not in body:
            missing.append("откат")
        if not re.search(r"(?i)изолирован|тестов", body):
            missing.append("изолированный тест")
        if "Разрешение владельца" not in body:
            missing.append("разрешение")
        if missing:
            bad.append(f"{p.name}: нет {', '.join(missing)}")
    if bad:
        add("П1 планы", "FAIL", "; ".join(bad[:5]))
    else:
        add("П1 планы", "OK", f"планов проверено: {len(plans) - 1}")


def check_root() -> None:
    extra = []
    for p in ROOT.iterdir():
        if p.is_file() and p.name not in ROOT_ALLOWED and not p.name.startswith("."):
            extra.append(p.name)
    if extra:
        add("П5 корень без свалки", "WARN", "лишние файлы в корне: " + ", ".join(sorted(extra)[:8]))
    else:
        add("П5 корень без свалки", "OK", "корень соответствует списку")


def check_violations() -> None:
    if not NARUSHENIYA.exists():
        add("П13 нарушения", "OK", "журнал нарушений пуст (файла нет)")
        return
    rows = [l for l in NARUSHENIYA.read_text("utf-8").splitlines() if l.startswith("| 20")]
    if len(rows) >= 3:
        add("П13 нарушения", "FAIL", f"{len(rows)} нарушения — требуется STOP")
    elif rows:
        add("П13 нарушения", "WARN", f"{len(rows)} из 3 нарушений")
    else:
        add("П13 нарушения", "OK", "нарушений нет")


def check_stop() -> None:
    add("П11 стоп-флаг", "FAIL" if STOP.exists() else "OK",
        "STOP включён — работа остановлена" if STOP.exists() else "не включён")


def check_obsidian() -> None:
    if not VAULT.exists():
        add("П9 итог в Obsidian", "SKIP", "хранилище недоступно")
        return
    today = date.today().isoformat()
    notes = [p for p in VAULT.rglob("*.md") if p.name.startswith(today)]
    if notes:
        add("П9 итог в Obsidian", "OK", f"заметок за {today}: {len(notes)}")
    else:
        add("П9 итог в Obsidian", "WARN", f"заметки за {today} нет")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()

    check_secrets()
    check_rules_changed()
    check_plans()
    check_root()
    check_violations()
    check_stop()
    check_obsidian()

    fails = [r for r in RESULTS if r["status"] == "FAIL"]
    if args.json:
        print(json.dumps({"checks": RESULTS, "fails": len(fails)}, ensure_ascii=False, indent=1))
    else:
        print("== Аудит правил ==")
        for r in RESULTS:
            print(f"{r['status']:<4} {r['rule']}: {r['detail']}")
        print(f"\nИтог: FAIL {len(fails)}, WARN {sum(1 for r in RESULTS if r['status'] == 'WARN')}, "
              f"OK {sum(1 for r in RESULTS if r['status'] == 'OK')}")
        if fails:
            print("Есть нарушения — запись в doktor/narusheniya.md, решение за владельцем.")
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
