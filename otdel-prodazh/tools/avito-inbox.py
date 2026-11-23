# -*- coding: utf-8 -*-
"""Читает чаты Авито по списку и присылает в Telegram карточки с перепиской.

Список чатов: otdel-prodazh/runtime/avito-chats.json
Формат: [{"id": "u2i-...", "name": "София", "item": "Букет на День матери"}]

    python3 otdel-prodazh/tools/avito-inbox.py           # только новые
    python3 otdel-prodazh/tools/avito-inbox.py --all     # все заново
"""
from __future__ import annotations

import json
import pathlib
import subprocess
import sys

ROOT = pathlib.Path(__file__).resolve().parents[2]
CHATS = ROOT / "otdel-prodazh" / "runtime" / "avito-chats.json"
STATE = ROOT / "otdel-prodazh" / "runtime" / "avito-inbox.json"
TG = ROOT / "agent-marketolog" / "bot" / "tg_client.py"
PORT = 9224
NODE = "/Applications/DeepSeek Harness.app/Contents/Resources/runtime/primary-runtime/dependencies/node/bin/node"

EXTRACT = r"""
(() => {
  const ms=[...document.querySelectorAll('[data-marker="message"]')].map(e=>{
    const cls=(e.className||'').toString();
    const dir = /right/.test(cls) ? 'out' : 'in';
    const t=e.innerText.replace(/\s+/g,' ').trim();
    return {dir, t};
  });
  const head=document.body.innerText.replace(/\s+/g,' ');
  return JSON.stringify({ms, head: head.slice(0, 300)});
})()
"""


def read_chat(ws: str, channel: str) -> dict:
    url = f"https://www.avito.ru/profile/messenger/channel/{channel}"
    script = f"""
const ws=new WebSocket({json.dumps(ws)});
let id=0;const pend=new Map();
ws.addEventListener('message',e=>{{const m=JSON.parse(e.data); if(m.id&&pend.has(m.id)){{const q=pend.get(m.id);pend.delete(m.id);q(m.result);}}}});
const send=(method,params={{}})=>new Promise(res=>{{const i=++id;pend.set(i,res);ws.send(JSON.stringify({{id:i,method,params}}));}});
const sleep=ms=>new Promise(r=>setTimeout(r,ms));
await new Promise(r=>ws.addEventListener('open',r,{{once:true}}));
await send('Page.navigate',{{url:{json.dumps(url)}}});
await sleep(10000);
const r=await send('Runtime.evaluate',{{expression:{json.dumps(EXTRACT)},returnByValue:true}});
console.log(r.result.value);
process.exit(0);
"""
    out = subprocess.run([NODE, "--input-type=module", "-e", script], capture_output=True, text=True, timeout=90)
    return json.loads(out.stdout or "{}")


def ws_url() -> str:
    import urllib.request
    with urllib.request.urlopen(f"http://localhost:{PORT}/json/list", timeout=5) as r:
        tabs = json.load(r)
    page = next((t for t in tabs if t.get("type") == "page" and "avito.ru" in (t.get("url") or "")), None)
    if not page:
        raise SystemExit("нет вкладки Авито")
    return page["webSocketDebuggerUrl"]


def tg(text: str) -> None:
    subprocess.run([sys.executable, str(TG), text], check=True, capture_output=True, timeout=40)


def main() -> int:
    if not CHATS.exists():
        print(f"нет списка чатов: {CHATS}")
        return 2
    chats = json.loads(CHATS.read_text())
    state = json.loads(STATE.read_text()) if STATE.exists() else {}
    ws = ws_url()
    show_all = "--all" in sys.argv
    sent = 0
    for c in chats:
        cid = c["id"]
        data = read_chat(ws, cid)
        ms = data.get("ms", [])
        if not ms:
            continue
        last_in = next((m for m in reversed(ms) if m["dir"] == "in"), None)
        if not last_in:
            continue
        if not show_all and state.get(cid) == last_in["t"]:
            continue
        dialog = "\n".join(
            ("👤 " if m["dir"] == "in" else "💬 ") + m["t"] for m in ms[-6:]
        )
        card = (
            f"🟦 Заявка Авито · {c.get('name') or 'клиент'}\n"
            f"Объявление: {c.get('item') or '—'}\n\n"
            f"Переписка:\n{dialog}\n\n"
            f"Ответить: «#{cid} ответ: ваш текст»"
        )
        tg(card)
        state[cid] = last_in["t"]
        sent += 1
        print(f"карточка: {c.get('name')} ({cid[:10]}…)")
    STATE.parent.mkdir(parents=True, exist_ok=True)
    STATE.write_text(json.dumps(state, ensure_ascii=False, indent=2))
    print(f"отправлено карточек: {sent}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
