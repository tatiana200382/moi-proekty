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
const focused = await send('Runtime.evaluate', {expression: `(()=>{const el=document.querySelector('[data-marker="reply/input"]'); if(!el) return false; el.focus(); const set=Object.getOwnPropertyDescriptor(window.HTMLTextAreaElement.prototype,'value').set; set.call(el, process_text); el.dispatchEvent(new Event('input',{bubbles:true})); return true;})()`.replace('process_text', JSON.stringify(process.argv[3])), returnByValue:true});
if (!focused.result.value) { console.log('НЕТ ПОЛЯ ВВОДА'); process.exit(2); }
await sleep(700);
for (const type of ['keyDown','char','keyUp']) {
  await send('Input.dispatchKeyEvent', {type, key:'Enter', code:'Enter', windowsVirtualKeyCode:13, nativeVirtualKeyCode:36, text: type==='char' ? '\r' : undefined});
  await sleep(120);
}
await sleep(3000);
const after = await send('Runtime.evaluate', {expression: `(()=>{const ms=[...document.querySelectorAll('[data-marker="message"]')]; const last=ms[ms.length-1]; return last?last.innerText.replace(/\s+/g,' ').slice(0,90):'нет сообщений';})()`, returnByValue:true});
console.log('ОТПРАВЛЕНО ' + JSON.stringify({last: after.result.value}));
process.exit(0);
"""



def log_to_max(text: str) -> None:
    """Копия отправленного ответа в чат MAX «Заявки», чтобы команда видела."""
    import os
    if os.environ.get("NO_MAX_LOG"):
        return
    try:
        import sys as _sys, pathlib as _pl
        _sys.path.insert(0, str(_pl.Path(__file__).resolve().parents[2] / "agent-marketolog" / "bot"))
        import max_client
        max_client.send(max_client.chat_id(), text)
    except Exception:
        pass



PREFIX_NOISE = ("черновик ответа:", "черновик:", "вы:", "ответ:")


def sanitize_outgoing(text: str) -> str:
    """Убирает служебные префиксы из текста, который уходит клиенту."""
    t = (text or "").strip()
    changed = True
    while changed:
        changed = False
        low = t.lower()
        for p in PREFIX_NOISE:
            if low.startswith(p):
                t = t[len(p):].strip()
                changed = True
    return t.strip()

def main() -> int:
    args = [a for a in sys.argv[1:]]
    dry = "--dry" in args
    if dry:
        args.remove("--dry")
    if len(args) < 2:
        print(__doc__)
        return 2
    channel, text = args[0], sanitize_outgoing(args[1])
    url = f"https://www.avito.ru/profile/messenger/channel/{channel}"
    if dry:
        print(f"[dry] отправил бы в {url}: {text[:80]}…")
        return 0
    ws = ws_url()
    node = "/Applications/DeepSeek Harness.app/Contents/Resources/runtime/primary-runtime/dependencies/node/bin/node"
    proc = subprocess.run([node, "--input-type=module", "-e", SCRIPT, ws, url, text],
                          capture_output=True, text=True, timeout=90)
    out = proc.stdout.strip() or proc.stderr.strip()
    print(out)
    if "ОТПРАВЛЕНО" in out:
        where = "Авито"
        log_to_max(f"✅ Ответ отправлен · {where}\n{text}")
    return 0 if "ОТПРАВЛЕНО" in (proc.stdout or "") else 1


if __name__ == "__main__":
    sys.exit(main())
