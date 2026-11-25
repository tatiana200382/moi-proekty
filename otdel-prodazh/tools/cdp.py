# -*- coding: utf-8 -*-
"""Работа с уже открытым браузером: ОДНА вкладка, без создания новых.

Правило: не больше двух окон/вкладок. Все задачи ходят через эту вкладку.

    python3 otdel-prodazh/tools/cdp.py open <url>
    python3 otdel-prodazh/tools/cdp.py js "<выражение>"
    python3 otdel-prodazh/tools/cdp.py tabs
"""
from __future__ import annotations

import json
import sys
import time
import urllib.request

PORT = 9224
OPENER = urllib.request.build_opener(urllib.request.ProxyHandler({}))
MAX_TABS = 2


def tabs() -> list[dict]:
    return [t for t in json.load(OPENER.open(f"http://127.0.0.1:{PORT}/json/list", timeout=10))
            if t.get("type") == "page"]


def pick() -> dict | None:
    ts = tabs()
    return ts[0] if ts else None


def ws_url() -> str:
    page = pick()
    if page:
        return page["webSocketDebuggerUrl"]
    # вкладок нет — открываем одну новую (и это единственная)
    req = urllib.request.Request(f"http://127.0.0.1:{PORT}/json/new?about:blank", method="PUT")
    return json.loads(OPENER.open(req, timeout=15).read())["webSocketDebuggerUrl"]


def connect():
    import websocket
    return websocket.create_connection(ws_url(), timeout=40)


def rpc(ws, method: str, params: dict | None = None, session: str | None = None):
    msg = {"id": getattr(rpc, "_i", 0) + 1, "method": method, "params": params or {}}
    rpc._i = msg["id"]
    if session:
        msg["sessionId"] = session
    ws.send(json.dumps(msg))
    while True:
        r = json.loads(ws.recv())
        if r.get("id") == msg["id"]:
            return r


def open_url(url: str, wait: float = 8.0) -> None:
    ws = connect()
    rpc(ws, "Page.navigate", {"url": url})
    time.sleep(wait)
    ws.close()


def js(expr: str):
    ws = connect()
    r = rpc(ws, "Runtime.evaluate", {"expression": expr, "returnByValue": True})
    ws.close()
    try:
        return r["result"]["result"].get("value")
    except Exception:
        return None


def main(argv: list[str]) -> int:
    cmd = argv[0] if argv else "tabs"
    if cmd == "tabs":
        ts = tabs()
        print("вкладок:", len(ts))
        for t in ts:
            print(" -", (t.get("url") or "")[:70])
        return 0
    if cmd == "open" and len(argv) > 1:
        open_url(argv[1])
        print("открыто в единственной вкладке:", argv[1][:70])
        return 0
    if cmd == "js" and len(argv) > 1:
        print(js(argv[1]))
        return 0
    print(__doc__)
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
