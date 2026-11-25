# -*- coding: utf-8 -*-
"""Отправка сообщения клиенту ВК через рабочий профиль браузера (CDP 9224).

    python3 otdel-prodazh/tools/vk-send.py <peer> "текст"
    python3 otdel-prodazh/tools/vk-send.py --check <peer>

Отличие от vk-reply-browser.py: сначала очищает поле ввода, потом вставляет текст,
проверяет, что сообщение появилось в диалоге, и только тогда считает отправку успешной.
"""
from __future__ import annotations

import json
import subprocess
import sys
import time
import urllib.request

PORT = 9224
NODE = "/Applications/DeepSeek Harness.app/Contents/Resources/runtime/primary-runtime/dependencies/node/bin/node"
BASE = "https://vk.ru/gim188108705/convo/"
OPENER = urllib.request.build_opener(urllib.request.ProxyHandler({}))

SCRIPT = r"""
const ws = new WebSocket(process.argv[1]);
const [url, text, mode] = [process.argv[2], process.argv[3], process.argv[4]];
let id = 0; const pend = new Map();
ws.addEventListener('message', e => { const m = JSON.parse(e.data); if (m.id && pend.has(m.id)) { pend.get(m.id)(m.result); pend.delete(m.id); } });
const send = (method, params = {}) => new Promise(res => { const i = ++id; pend.set(i, res); ws.send(JSON.stringify({ id: i, method, params })); });
const sleep = ms => new Promise(r => setTimeout(r, ms));
await new Promise(r => ws.addEventListener('open', r, { once: true }));
await send('Page.navigate', { url });
await sleep(9000); await send('Runtime.evaluate', { expression: "window.scrollTo(0, document.body.scrollHeight)", returnByValue: true }); await sleep(1500);
const clear = `(() => {
  const sels = ['.ComposerInput__input', '[contenteditable="true"]', 'div[role="textbox"]', '.ConvoComposer textarea', 'textarea'];
  for (let i = 0; i < 30; i++) {
    for (const s of sels) {
      const el = document.querySelector(s);
      if (el) { el.focus(); document.execCommand('selectAll'); document.execCommand('delete'); return 'ok'; }
    }
  }
  return 'нет поля';
})()`;
const r1 = await send('Runtime.evaluate', { expression: clear, returnByValue: true });
if (!r1 || r1.value !== 'ok') { console.log('ПОЛЕ НЕ НАЙДЕНО'); process.exit(1); }
if (mode === 'check') { console.log('ПОЛЕ НАЙДЕНО'); process.exit(0); }
await send('Input.insertText', { text });
await sleep(400);
await send('Input.dispatchKeyEvent', { type: 'keyDown', key: 'Enter', code: 'Enter', windowsVirtualKeyCode: 13, nativeVirtualKeyCode: 36 });
await send('Input.dispatchKeyEvent', { type: 'keyUp', key: 'Enter', code: 'Enter', windowsVirtualKeyCode: 13, nativeVirtualKeyCode: 36 });
await sleep(2500);
const probe = `(() => { const t = ${JSON.stringify(text.slice(0, 40))}; const nodes = [...document.querySelectorAll('.ConvoMessage, [class*="ConvoMessage"]')]; const hit = nodes.some(n => (n.innerText || '').includes(t)); const box = document.querySelector('.ComposerInput__input'); return JSON.stringify({hit, box: box ? (box.innerText || '').slice(0, 40) : ''}); })()`;
const r2 = await send('Runtime.evaluate', { expression: probe, returnByValue: true });
console.log('РЕЗУЛЬТАТ ' + (r2 && r2.value ? r2.value : '{}'));
process.exit(0);
"""


def ws_url() -> str:
    with OPENER.open(f"http://127.0.0.1:{PORT}/json/version", timeout=5) as r:
        return json.load(r)["webSocketDebuggerUrl"]


def main() -> int:
    args = sys.argv[1:]
    mode = "check" if "--check" in args else "send"
    args = [a for a in args if a != "--check"]
    if not args:
        print(__doc__)
        return 2
    peer = args[0]
    text = args[1] if len(args) > 1 else ""
    proc = subprocess.run([NODE, "--input-type=module", "-e", SCRIPT, ws_url(), BASE + peer, text, mode],
                          capture_output=True, text=True, timeout=120)
    out = (proc.stdout or proc.stderr).strip()
    print(out)
    if mode == "check":
        return 0 if "ПОЛЕ НАЙДЕНО" in out else 1
    try:
        res = json.loads(out.split("РЕЗУЛЬТАТ ", 1)[1])
    except Exception:
        return 1
    return 0 if res.get("hit") and not res.get("box") else 1


if __name__ == "__main__":
    sys.exit(main())
