#!/usr/bin/env python3
"""Выгружает cookie Авито из Chrome на Маке и обновляет сессию на сервере."""
import base64, pathlib, subprocess, sys, datetime

HOME = pathlib.Path.home()
DIR = pathlib.Path(__file__).resolve().parent
STATE = pathlib.Path("/tmp/avito-mac-state.json")
LOG = pathlib.Path("/tmp/avito-sync.log")
SERVER_STATE = "/home/tanya/sales/states/avito.json"


def log(msg: str) -> None:
    with open(LOG, "a", encoding="utf-8") as f:
        f.write(f"{datetime.datetime.now():%F %T} {msg}\n")


try:
    subprocess.run(["/usr/local/bin/node", str(DIR / "avito-cookies.mjs")],
                   capture_output=True, timeout=90)
except Exception as e:
    log("node: " + str(e)[:120])
if not STATE.exists() or STATE.stat().st_size < 5000:
    log("нет свежего state")
    sys.exit(1)

b64 = base64.b64encode(STATE.read_bytes()).decode()
cmd = (f"echo {b64} | base64 -d > {SERVER_STATE}.new && "
       f"chmod 600 {SERVER_STATE}.new && mv {SERVER_STATE}.new {SERVER_STATE}")
try:
    r = subprocess.run([str(HOME / "bin" / "domashniy"), cmd],
                       capture_output=True, text=True, timeout=180)
    log(f"upload rc={r.returncode} size={STATE.stat().st_size}")
except subprocess.TimeoutExpired:
    log("upload timeout")
    sys.exit(1)
