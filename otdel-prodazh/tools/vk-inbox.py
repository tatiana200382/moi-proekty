# -*- coding: utf-8 -*-
"""Читает диалоги сообщества ВК и присылает карточки в чат MAX «Заявки».

    python3 otdel-prodazh/tools/vk-inbox.py            # новые
    python3 otdel-prodazh/tools/vk-inbox.py --all      # все заново
"""
from __future__ import annotations

import json
import pathlib
import subprocess
import sys

ROOT = pathlib.Path(__file__).resolve().parents[2]
STATE = ROOT / "otdel-prodazh" / "runtime" / "vk-inbox.json"
sys.path.insert(0, str(ROOT / "agent-marketolog" / "bot"))
PORT = 9224
NODE = "/Applications/DeepSeek Harness.app/Contents/Resources/runtime/primary-runtime/dependencies/node/bin/node"

JS = r"""
(() => {
  const items=[...document.querySelectorAll('[data-testid="vkme_convo_list_item"]')];
  return JSON.stringify(items.map(e=>({peer:e.getAttribute('data-peer-id')||'', txt:e.innerText.replace(/\s+/g,' ').trim()})));
})()
"""


def read_dialogs() -> list[dict]:
    import urllib.request

OPENER = urllib.request.build_opener(urllib.request.ProxyHandler({}))
    with OPENER.open(f"http://127.0.0.1:{PORT}/json/list", timeout=5) as r:
        tabs = json.load(r)
    page = next((t for t in tabs if t.get("type") == "page" and "vk" in (t.get("url") or "")), None)
    if not page:
        raise SystemExit("нет вкладки ВК")
    script = f"""
const ws=new WebSocket({json.dumps(page['webSocketDebuggerUrl'])});
let id=0;const pend=new Map();
ws.addEventListener('message',e=>{{const m=JSON.parse(e.data); if(m.id&&pend.has(m.id)){{const q=pend.get(m.id);pend.delete(m.id);q(m.result);}}}});
const send=(method,params={{}})=>new Promise(res=>{{const i=++id;pend.set(i,res);ws.send(JSON.stringify({{id:i,method,params}}));}});
const sleep=ms=>new Promise(r=>setTimeout(r,ms));
await new Promise(r=>ws.addEventListener('open',r,{{once:true}}));
await send('Page.navigate',{{url:'https://vk.ru/gim188108705'}});
await sleep(9000);
const r=await send('Runtime.evaluate',{{expression:{json.dumps(JS)},returnByValue:true}});
console.log(r.result.value);
process.exit(0);
"""
    out = subprocess.run([NODE, "--input-type=module", "-e", script], capture_output=True, text=True, timeout=90)
    return json.loads(out.stdout or "[]")


def send_max(text: str) -> None:
    import max_client
    max_client.send(max_client.chat_id(), text)


def main() -> int:
    show_all = "--all" in sys.argv
    dialogs = read_dialogs()
    state = json.loads(STATE.read_text()) if STATE.exists() else {}
    sent = 0
    for d in dialogs:
        peer, txt = d.get("peer"), (d.get("txt") or "").strip()
        if not peer or not txt:
            continue
        if not show_all and state.get(peer) == txt:
            continue
        card = (
            f"🟪 Заявка ВКонтакте\n"
            f"Клиент: {txt.split(' ')[0] if txt else '—'}\n"
            f"Последнее сообщение: {txt[:250]}\n\n"
            f"Ответить: «#{peer} ответ: ваш текст»"
        )
        send_max(card)
        state[peer] = txt
        sent += 1
        print(f"карточка ВК: {peer}")
    STATE.parent.mkdir(parents=True, exist_ok=True)
    STATE.write_text(json.dumps(state, ensure_ascii=False, indent=2))
    print(f"всего карточек: {sent}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
