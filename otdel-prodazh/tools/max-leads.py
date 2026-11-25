# -*- coding: utf-8 -*-
"""Входящие из MAX → заявки в общий журнал.

Клиент пишет боту или в чат в MAX — скрипт делает файл заявки
в agent-marketolog/leads/, откуда его забирает sales_pipeline.

    python3 otdel-prodazh/tools/max-leads.py          # один проход
    python3 otdel-prodazh/tools/max-leads.py --watch  # каждые 30 секунд
"""
from __future__ import annotations

import json
import os
import pathlib
import re
import sys
import time
from datetime import datetime, timezone, timedelta

ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "agent-marketolog" / "bot"))

import max_client  # noqa: E402

LEADS_DIR = ROOT / "agent-marketolog" / "leads"
STATE = ROOT / "otdel-prodazh" / "runtime" / "max-leads.json"
MSK = timezone(timedelta(hours=3))

PHONE_RE = re.compile(r"(?:\+7|8)[\s\-()]*\d{3}[\s\-()]*\d{3}[\s\-]*\d{2}[\s\-]*\d{2}")


def load_state() -> dict:
    if STATE.exists():
        try:
            return json.loads(STATE.read_text())
        except Exception:
            pass
    return {"marker": None, "seen": []}


def save_state(state: dict) -> None:
    STATE.parent.mkdir(parents=True, exist_ok=True)
    state["seen"] = state["seen"][-500:]
    STATE.write_text(json.dumps(state, ensure_ascii=False, indent=1))


def bot_id() -> int:
    try:
        return int(max_client.me().get("user_id") or 0)
    except Exception:
        return 0


def _sender_name(msg: dict) -> str:
    sender = msg.get("sender") or {}
    return (sender.get("name") or sender.get("username") or "").strip() or "Клиент MAX"


def _is_ours(msg: dict, me: int) -> bool:
    sender = msg.get("sender") or {}
    return int(sender.get("user_id") or 0) == me or bool(sender.get("is_bot"))


def make_lead(msg: dict, me: int) -> dict | None:
    body = msg.get("body") or {}
    text = (body.get("text") or "").strip()
    if not text or _is_ours(msg, me):
        return None
    sender = msg.get("sender") or {}
    uid = sender.get("user_id")
    mid = body.get("mid") or ""
    phone = ""
    m = PHONE_RE.search(text)
    if m:
        phone = m.group(0)
    now = datetime.now(MSK)
    return {
        "source": "max",
        "client": _sender_name(msg),
        "question": text[:1500],
        "answer": "",
        "status": "новая",
        "created": now.isoformat(timespec="seconds"),
        "link": "",
        "external_id": f"{uid}:{mid[-12:]}" if uid and mid else "",
        "contact": phone,
        "email": "",
        "amount": "",
        "items": [],
        "comment": "пришло из MAX",
        "notified": False,
        "sent_at": "",
        "max_mid": mid,
        "max_user_id": uid,
        "baseline": False,
        "_file": f"{now.strftime('%Y%m%dT%H%M%S')}-max-{str(uid)}-{mid[-8:] or 'x'}.json",
    }


def save_lead(lead: dict) -> pathlib.Path:
    LEADS_DIR.mkdir(parents=True, exist_ok=True)
    name = lead.pop("_file")
    path = LEADS_DIR / name
    path.write_text(json.dumps(lead, ensure_ascii=False, indent=1))
    return path


def once() -> tuple[int, int]:
    state = load_state()
    me = bot_id()
    try:
        data = max_client.updates(marker=state.get("marker"), limit=100, timeout=10)
    except Exception as exc:
        print(f"MAX недоступен: {exc}")
        return 0, 0
    ups = data.get("updates") or []
    created = 0
    seen = set(state.get("seen") or [])
    for up in ups:
        msg = ((up.get("message") or up.get("body")) if isinstance(up, dict) else None) or {}
        mid = (msg.get("body") or {}).get("mid") or ""
        lead = make_lead(msg, me) if msg else None
        if lead and mid not in seen:
            save_lead(dict(lead))
            seen.add(mid)
            created += 1
            print(f"+ заявка MAX: {lead['client']} — {(lead['question'] or '')[:50]}")
    marker = data.get("marker") or state.get("marker")
    state["marker"] = marker
    state["seen"] = list(seen)
    save_state(state)
    return created, len(ups)


def main(argv: list[str]) -> int:
    watch = "--watch" in argv
    while True:
        created, total = once()
        print(f"апдейтов: {total}, новых заявок: {created}")
        if not watch:
            return 0
        time.sleep(30)


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
