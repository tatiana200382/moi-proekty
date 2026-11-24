# -*- coding: utf-8 -*-
"""Простой сторож на сервере: отвечает, что опрос жив.

    python3 health-server.py            # слушает 0.0.0.0:8790
    curl http://сервер:8790/health      # {"ok": true, "last_run": "..."}

Файл-отметка обновляется в run.sh после успешного опроса.
"""
from __future__ import annotations

import json
import os
import pathlib
import time
from http.server import BaseHTTPRequestHandler, HTTPServer

ROOT = pathlib.Path(__file__).resolve().parents[2]
MARK = ROOT / "otdel-prodazh" / "runtime" / "last-run.txt"
PORT = int(os.environ.get("HEALTH_PORT", "8790"))
STALE_MIN = int(os.environ.get("HEALTH_STALE_MIN", "45"))


class Handler(BaseHTTPRequestHandler):
    def do_GET(self):  # noqa: N802
        if self.path.split("?")[0] not in ("/health", "/"):
            self.send_response(404); self.end_headers(); return
        last = MARK.read_text(encoding="utf-8").strip() if MARK.exists() else ""
        age = None
        if last:
            try:
                age = round((time.time() - float(last)) / 60, 1)
            except ValueError:
                age = None
        ok = age is not None and age <= STALE_MIN
        body = json.dumps({"ok": ok, "last_run": last, "minutes_ago": age, "stale_min": STALE_MIN},
                          ensure_ascii=False).encode()
        self.send_response(200)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, *args):  # тихо
        pass


if __name__ == "__main__":
    print(f"сторож на :{PORT}, отметка {MARK}")
    HTTPServer(("0.0.0.0", PORT), Handler).serve_forever()
