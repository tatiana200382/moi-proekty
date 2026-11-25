# -*- coding: utf-8 -*-
"""Отвечает клиенту ВКонтакте через браузер (без токена).

Нужен открытый Chrome с отладкой на 9224 и залогиненный ВК.

    python3 otdel-prodazh/tools/vk-reply-browser.py 874290198 "текст"
    python3 otdel-prodazh/tools/vk-reply-browser.py --check 874290198
"""
from __future__ import annotations

import json
import subprocess
import sys
import urllib.request

OPENER = urllib.request.build_opener(urllib.request.ProxyHandler({}))

PORT = 9224
NODE = "/Applications/DeepSeek Harness.app/Contents/Resources/runtime/primary-runtime/dependencies/node/bin/node"
BASE = "https://vk.ru/gim188108705/convo/"


def ws_url() -> str:
    with OPENER.open(f"http://127.0.0.1:{PORT}/json/list", timeout=5) as r:
        tabs = json.load(r)
    page = next((t for t in tabs if t.get("type") == "page" and "vk" in (t.get("url") or "")), None)
    if not page:
        raise SystemExit("нет вкладки ВК в управляемом Chrome")
    return page["webSocketDebuggerUrl"]


SCRIPT = r"""
const ws=new WebSocket(process.argv[1]);
let id=0;const pend=new Map();
ws.addEventListener('message',e=>{const m=JSON.parse(e.data); if(m.id&&pend.has(m.id)){const q=pend.get(m.id);pend.delete(m.id);q(m.result);}});
const send=(method,params={})=>new Promise(res=>{const i=++id;pend.set(i,res);ws.send(JSON.stringify({id:i,method,params}));});
const sleep=ms=>new Promise(r=>setTimeout(r,ms));
await new Promise(r=>ws.addEventListener('open',r,{once:true}));
await send('Page.navigate',{url:process.argv[2]});
await sleep(9000);
const found=await send('Runtime.evaluate',{expression:`(()=>{const el=document.querySelector('.ComposerInput__input, [contenteditable="true"]'); if(!el) return false; el.focus(); return true;})()`,returnByValue:true});
if(!found.result.value){ console.log('НЕТ ПОЛЯ ВВОДА'); process.exit(2); }
if(process.argv[4]==='check'){ console.log('ПОЛЕ НАЙДЕНО'); process.exit(0); }
await send('Input.insertText',{text:process.argv[3]});
await sleep(700);
await send('Input.dispatchKeyEvent',{type:'keyDown',key:'Enter',code:'Enter',windowsVirtualKeyCode:13,nativeVirtualKeyCode:36});
await send('Input.dispatchKeyEvent',{type:'keyUp',key:'Enter',code:'Enter',windowsVirtualKeyCode:13,nativeVirtualKeyCode:36});
await sleep(2500);
const left=await send('Runtime.evaluate',{expression:`(()=>{const el=document.querySelector('.ComposerInput__input'); return el?el.innerText.slice(0,60):'ок';})()`,returnByValue:true});
console.log('ОТПРАВЛЕНО', JSON.stringify(left.result.value));
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
    args = sys.argv[1:]
    mode = "check" if "--check" in args else "send"
    args = [a for a in args if a != "--check"]
    if len(args) < 1 or (mode == "send" and len(args) < 2):
        print(__doc__)
        return 2
    peer = args[0]
    text = sanitize_outgoing(args[1] if len(args) > 1 else "")
    proc = subprocess.run([NODE, "--input-type=module", "-e", SCRIPT, ws_url(), BASE + peer, text, mode],
                          capture_output=True, text=True, timeout=90)
    out = (proc.stdout or proc.stderr).strip()
    print(out)
    if mode == "check":
        return 0 if "ПОЛЕ НАЙДЕНО" in out else 1
    return 0 if "ОТПРАВЛЕНО" in out else 1


if __name__ == "__main__":
    sys.exit(main())
