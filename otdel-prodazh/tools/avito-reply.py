# -*- coding: utf-8 -*-
"""Отправляет ответ в чат Авито от имени владельца (через его Chrome).

Использование:
    python3 otdel-prodazh/tools/avito-reply.py <channel_id> "текст ответа"
    python3 otdel-prodazh/tools/avito-reply.py --dry <channel_id> "текст"

channel_id — хвост ссылки чата, например u2i-5hMiYZ042l5YPNlI20tm2A
"""
from __future__ import annotations

import json
import subprocess
import sys
import time
import urllib.request

PORT = 9224
NODE_HINT = "нужен Chrome с отладкой на порту 9224"


def ws_url() -> str:
    with urllib.request.urlopen(f"http://localhost:{PORT}/json/list", timeout=5) as r:
        tabs = json.load(r)
    page = next((t for t in tabs if t.get("type") == "page" and "avito.ru" in (t.get("url") or "")), None)
    if not page:
        raise SystemExit("нет вкладки Авито в управляемом Chrome")
    return page["webSocketDebuggerUrl"]


SCRIPT = r"""
const ws = new WebSocket(process.argv[1]);
let id = 0; const pend = new Map();
ws.addEventListener('message', e => { const m = JSON.parse(e.data); if (m.id && pend.has(m.id)) { const q = pend.get(m.id); pend.delete(m.id); q(m.result); } });
const send = (method, params={}) => new Promise(res => { const i = ++id; pend.set(i, res); ws.send(JSON.stringify({id:i, method, params})); });
const sleep = ms => new Promise(r => setTimeout(r, ms));
await new Promise(r => ws.addEventListener('open', r, {once:true}));
await send('Page.navigate', {url: process.argv[2]});
await sleep(9000);
const focused = await send('Runtime.evaluate', {expression: `(()=>{const el=document.querySelector('[data-marker="reply/input"]'); if(!el) return false; el.focus(); const r=el.getBoundingClientRect(); window.__cx=Math.round(r.x+r.width/2); window.__cy=Math.round(r.y+r.height/2); return true;})()`, returnByValue:true});
if (!focused.result.value) { console.log('НЕТ ПОЛЯ ВВОДА'); process.exit(2); }
await send('Input.insertText', {text: process.argv[3]});
await sleep(900);
const clicked = await send('Runtime.evaluate', {expression: `(()=>{const b=document.querySelector('[data-marker="reply/send"]'); if(!b) return 'нет кнопки'; b.click(); return 'нажал';})()`, returnByValue:true});
await sleep(2500);
const after = await send('Runtime.evaluate', {expression: `(()=>{const ms=[...document.querySelectorAll('[data-marker="message"]')]; const last=ms[ms.length-1]; return last?last.innerText.replace(/\\s+/g,' ').slice(0,80):'нет сообщений';})()`, returnByValue:true});
console.log('ОТПРАВЛЕНО ' + JSON.stringify({button: clicked.result.value, last: after.result.value}));
process.exit(0);
"""


def main() -> int:
    args = [a for a in sys.argv[1:]]
    dry = "--dry" in args
    if dry:
        args.remove("--dry")
    if len(args) < 2:
        print(__doc__)
        return 2
    channel, text = args[0], args[1]
    url = f"https://www.avito.ru/profile/messenger/channel/{channel}"
    if dry:
        print(f"[dry] отправил бы в {url}: {text[:80]}…")
        return 0
    ws = ws_url()
    node = "/Applications/DeepSeek Harness.app/Contents/Resources/runtime/primary-runtime/dependencies/node/bin/node"
    proc = subprocess.run([node, "--input-type=module", "-e", SCRIPT, ws, url, text],
                          capture_output=True, text=True, timeout=90)
    print(proc.stdout.strip() or proc.stderr.strip())
    return 0 if "ОТПРАВЛЕНО" in (proc.stdout or "") else 1


if __name__ == "__main__":
    sys.exit(main())
