"""Общие пути и настройки для всех шагов сборки базы контактов."""
import json
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SCRIPTS = ROOT / "scripts"
DATA = ROOT / "data"
PHONE_DIR = DATA / "phone"
TG_DIR = ROOT / "tg"
OUTPUT = ROOT / "output"
CONFIG_PATH = ROOT / "config.json"

for _d in (DATA, PHONE_DIR, TG_DIR, OUTPUT):
    _d.mkdir(parents=True, exist_ok=True)

DEFAULT_CONFIG = {
    "owner_name": "",
    "output_name": "База_контактов",
    "phone": {"enabled": True, "adb_path": "adb"},
    "telegram": {
        "enabled": True,
        "api_id": 2040,
        "api_hash": "b18441a1ff607e10a989891a5462e627",
        "sessions": ["main"],
        "chats": [],
    },
}


def load_config():
    if CONFIG_PATH.exists():
        try:
            cfg = json.loads(CONFIG_PATH.read_text(encoding="utf-8"))
        except Exception:
            cfg = {}
    else:
        cfg = {}
    merged = json.loads(json.dumps(DEFAULT_CONFIG))
    for k, v in cfg.items():
        if isinstance(v, dict) and isinstance(merged.get(k), dict):
            merged[k].update(v)
        else:
            merged[k] = v
    return merged


def save_config(cfg):
    CONFIG_PATH.write_text(json.dumps(cfg, ensure_ascii=False, indent=2), encoding="utf-8")


def say(msg=""):
    print(msg, flush=True)


def head(title):
    say("")
    say("=" * 64)
    say(title)
    say("=" * 64)


def fail(msg):
    say("")
    say("!! " + msg)
    sys.exit(1)
