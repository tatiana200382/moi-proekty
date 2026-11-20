#!/usr/bin/env node
// Диагностика клика: открыть страницу, найти элемент, показать что под точкой,
// кликнуть мышью и вернуть состояние ДО/ПОСЛЕ. Только для чтения списков.
// node cdp-clicktest.mjs <url> <css-селектор>
const [, , url, selector] = process.argv;
const PORT = process.env.CDP_PORT || 9224;
const sleep = (ms) => new Promise((r) => setTimeout(r, ms));

const ver = await (await fetch(`http://127.0.0.1:${PORT}/json/version`)).json();
const ws = new WebSocket(ver.webSocketDebuggerUrl);
await new Promise((res, rej) => {
  ws.addEventListener("open", res, { once: true });
  ws.addEventListener("error", rej, { once: true });
});
let id = 0;
const pending = new Map();
ws.addEventListener("message", (ev) => {
  const m = JSON.parse(ev.data);
  if (m.id && pending.has(m.id)) {
    const { resolve, reject } = pending.get(m.id);
    pending.delete(m.id);
    m.error ? reject(new Error(JSON.stringify(m.error))) : resolve(m.result);
  }
});
const send = (method, params = {}, sessionId) =>
  new Promise((resolve, reject) => {
    const mid = ++id;
    pending.set(mid, { resolve, reject });
    const msg = { id: mid, method, params };
    if (sessionId) msg.sessionId = sessionId;
    ws.send(JSON.stringify(msg));
    setTimeout(() => pending.has(mid) && (pending.delete(mid), reject(new Error("таймаут " + method))), 60000);
  });

const { targetId } = await send("Target.createTarget", { url: "about:blank" });
const { sessionId } = await send("Target.attachToTarget", { targetId, flatten: true });
await send("Page.enable", {}, sessionId);
await send("Page.navigate", { url }, sessionId);
await sleep(9000);

const ev = async (expr) => {
  const r = await send("Runtime.evaluate", { expression: expr, returnByValue: true, awaitPromise: true }, sessionId);
  return r?.result?.value;
};

const before = await ev(`document.querySelectorAll('[data-marker^="item-snippet/"]').length`);
const info = await ev(`(() => {
  const el = document.querySelector(${JSON.stringify(selector)});
  if (!el) return { found: false };
  el.scrollIntoView({ block: 'center' });
  const r = el.getBoundingClientRect();
  const x = r.x + r.width / 2, y = r.y + r.height / 2;
  const at = document.elementFromPoint(x, y);
  return { found: true, x, y, w: r.width, h: r.height,
    at: at ? (at.outerHTML || '').slice(0, 160) : null,
    same: at === el || el.contains(at) };
})()`);
console.log("до:", before, "элемент:", JSON.stringify(info));

if (info?.found) {
  await send("Input.dispatchMouseEvent", { type: "mouseMoved", x: info.x, y: info.y, buttons: 0 }, sessionId);
  await sleep(300);
  await send("Input.dispatchMouseEvent", { type: "mousePressed", x: info.x, y: info.y, button: "left", buttons: 1, clickCount: 1 }, sessionId);
  await sleep(80);
  await send("Input.dispatchMouseEvent", { type: "mouseReleased", x: info.x, y: info.y, button: "left", buttons: 0, clickCount: 1 }, sessionId);
  await sleep(500);
  console.log("через 0.5с:", await ev(`[...document.querySelectorAll('[data-marker^="profile-items-tab/tab"]')].map(b=>b.innerText.replace(/\\s+/g,' ')+(b.getAttribute('aria-selected')==='true'?'*':'')).join(' | ')`));
  await sleep(4000);
  console.log("через 4.5с:", await ev(`[...document.querySelectorAll('[data-marker^="profile-items-tab/tab"]')].map(b=>b.innerText.replace(/\\s+/g,' ')+(b.getAttribute('aria-selected')==='true'?'*':'')).join(' | ')`));
  console.log("карточек:", await ev(`document.querySelectorAll('[data-marker^="item-snippet/"]').length`));
  console.log("url:", await ev(`location.href`));
}
await send("Target.closeTarget", { targetId });
ws.close();
setTimeout(() => process.exit(0), 200);
