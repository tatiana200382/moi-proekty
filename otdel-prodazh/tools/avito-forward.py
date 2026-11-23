# -*- coding: utf-8 -*-
"""Присылает в Telegram карточки новых сообщений из чатов Авито.

Каждая карточка содержит номер заявки (channel id), объявление, текст клиента
и подсказку, как ответить. Запуск по расписанию вместе с watch/run.sh.

    python3 otdel-prodazh/tools/avito-forward.py            # отправить новые
    python3 otdel-prodazh/tools/avito-forward.py --all      # все чаты (для проверки)
"""
from __future__ import annotations

import json
import pathlib
import sys
import urllib.request

ROOT = pathlib.Path(__file__).resolve().parents[2]
STATE = ROOT / "otdel-prodazh" / "runtime" / "avito-forward.json"
TG = ROOT / "agent-marketolog" / "bot" / "tg_client.py"
PORT = 9224

JS = r"""
(() => {
  const links=[...document.querySelectorAll('[data-marker="channels/channelLink"]')];
  const seen=new Set(); const out=[];
  const text=(root,m)=>{const el=root.querySelector('[data-marker="'+m+'"]'); return el?el.innerText.trim():'';};
  for (const link of links) {
    const h=link.getAttribute('href')||'';
    if(!h||seen.has(h)) continue; seen.add(h);
    const row=link.closest('[data-marker="channels/channel"]')||link.parentElement;
    out.push({href:h, user:row?text(row,'channels/user-title'):'', item:row?text(row,'channels/item-title'):'', last:row?text(row,'channels/last-message'):''});
  }
  return JSON.stringify(out);
})()
"""


def collect() -> list[dict]:
    with urllib.request.urlopen(f"http://localhost:{PORT}/json/list", timeout=5) as r:
        tabs = json.load(r)
    page = next((t for t in tabs if t.get("type") == "page" and "avito.ru" in (t.get("url") or "")), None)
    if not page:
        raise SystemExit("нет вкладки Авито")
    import subprocess
    node = "/Applications/DeepSeek Harness.app/Contents/Resources/runtime/primary-runtime/dependencies/node/bin/node"
    script = f"""
const ws=new WebSocket({json.dumps(page['webSocketDebuggerUrl'])});
let id=0;const pend=new Map();
ws.addEventListener('message',e=>{{const m=JSON.parse(e.data); if(m.id&&pend.has(m.id)){{const q=pend.get(m.id);pend.delete(m.id);q(m.result);}}}});
const send=(method,params={{}})=>new Promise(res=>{{const i=++id;pend.set(i,res);ws.send(JSON.stringify({{id:i,method,params}}));}});
const sleep=ms=>new Promise(r=>setTimeout(r,ms));
await new Promise(r=>ws.addEventListener('open',r,{{once:true}}));
await send('Page.navigate',{{url:'https://www.avito.ru/profile/messenger'}});
await sleep(11000);
const r=await send('Runtime.evaluate',{{expression:{json.dumps(JS)},returnByValue:true}});
console.log(r.result.value);
process.exit(0);
"""
    out = subprocess.run([node, "--input-type=module", "-e", script], capture_output=True, text=True, timeout=90)
    return json.loads(out.stdout or "[]")


def send_telegram(text: str) -> None:
    import subprocess
    py = sys.executable
    subprocess.run([py, str(TG), text], check=True, capture_output=True, timeout=40)


def main() -> int:
    show_all = "--all" in sys.argv
    chats = collect()
    seen = json.loads(STATE.read_text()) if STATE.exists() else {}
    sent = 0
    allow = ("букет", "доставка цветов", "авторские букеты")
    uniq = set()
    for c in chats:
        cid = (c.get("href") or "").rstrip("/").split("/")[-1]
        last = (c.get("last") or "").strip()
        item = (c.get("item") or "").lower()
        if not cid or not last:
            continue
        if allow and not any(a in item for a in allow):
            continue
        key = (c.get("user") or "", item, last)
        if key in uniq:
            continue
        uniq.add(key)
        if not show_all and seen.get(cid) == last:
            continue
        card = (
            f"🟦 Новое сообщение · Авито\n"
            f"Объявление: {c.get('item') or '—'}\n"
            f"Клиент: {c.get('user') or '—'}\n"
            f"Текст: {last}\n\n"
            f"Ответить: «#{cid} ответ: ваш текст»\n"
            f"Номер заявки: {cid}"
        )
        send_telegram(card)
        seen[cid] = last
        sent += 1
    STATE.parent.mkdir(parents=True, exist_ok=True)
    STATE.write_text(json.dumps(seen, ensure_ascii=False, indent=2))
    print(f"отправлено карточек: {sent} из чатов {len(chats)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
