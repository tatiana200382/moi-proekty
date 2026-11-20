#!/usr/bin/env node
// Снимок страницы через CDP в ОТДЕЛЬНОЙ вкладке — только чтение.
// Ничего не нажимает, чужие вкладки не трогает: открыл свою, снял данные, закрыл.
//
// Использование:
//   node cdp-snimok.mjs <url> <out.json> [js-файл] [ожидание_ms]
//
// js-файл — выражение, которое вернёт данные (например tools/js/dump.js).
// По умолчанию снимает title, url, текст страницы и ссылки.
//
// Порт берётся из CDP_PORT (по умолчанию 9224).

import fs from "node:fs/promises";

const args = process.argv.slice(2);
const clickArg = args.find((a) => a.startsWith("--click="));
const rest = args.filter((a) => !a.startsWith("--click="));
const [url, outFile, jsFile, waitArg] = rest;
const clickSelector = clickArg ? clickArg.slice("--click=".length) : null;
if (!url || !outFile) {
  console.error(
    "использование: node cdp-snimok.mjs <url> <out.json> [js] [waitMs] [--click=<css>]"
  );
  process.exit(1);
}
const PORT = process.env.CDP_PORT || 9224;
const waitMs = Number(waitArg) || 8000;

const ver = await (await fetch(`http://127.0.0.1:${PORT}/json/version`)).json();
const ws = new WebSocket(ver.webSocketDebuggerUrl);
await new Promise((res, rej) => {
  ws.addEventListener("open", res, { once: true });
  ws.addEventListener("error", rej, { once: true });
});

let id = 0;
const pending = new Map();
ws.addEventListener("message", (ev) => {
  const msg = JSON.parse(ev.data);
  if (msg.id && pending.has(msg.id)) {
    const { resolve, reject } = pending.get(msg.id);
    pending.delete(msg.id);
    msg.error ? reject(new Error(JSON.stringify(msg.error))) : resolve(msg.result);
  }
});
const send = (method, params = {}, sessionId) =>
  new Promise((resolve, reject) => {
    const mid = ++id;
    pending.set(mid, { resolve, reject });
    const msg = { id: mid, method, params };
    if (sessionId) msg.sessionId = sessionId;
    ws.send(JSON.stringify(msg));
    setTimeout(() => {
      if (pending.has(mid)) {
        pending.delete(mid);
        reject(new Error(`таймаут ${method}`));
      }
    }, 60000);
  });
const sleep = (ms) => new Promise((r) => setTimeout(r, ms));

let targetId;
try {
  ({ targetId } = await send("Target.createTarget", { url: "about:blank" }));
  const { sessionId } = await send("Target.attachToTarget", { targetId, flatten: true });
  await send("Page.enable", {}, sessionId);
  await send("Page.navigate", { url }, sessionId);
  await sleep(waitMs);

  // прокрутка — чтобы подгрузились ленивые карточки
  for (let i = 0; i < 4; i++) {
    await send("Runtime.evaluate", { expression: "window.scrollTo(0, document.body.scrollHeight)" }, sessionId);
    await sleep(1200);
  }
  await send("Runtime.evaluate", { expression: "window.scrollTo(0, 0)" }, sessionId);

  if (clickSelector) {
    // настоящий клик мышью: React-кнопки не всегда реагируют на el.click()
    const rect = await send(
      "Runtime.evaluate",
      {
        expression: `(() => { const el = document.querySelector(${JSON.stringify(
          clickSelector
        )}); if (!el) return null; const r = el.getBoundingClientRect(); return { x: r.x + r.width/2, y: r.y + r.height/2 }; })()`,
        returnByValue: true,
      },
      sessionId
    );
    const p = rect?.result?.value;
    if (p) {
      await send("Input.dispatchMouseEvent", { type: "mouseMoved", x: p.x, y: p.y }, sessionId);
      await send("Input.dispatchMouseEvent", { type: "mousePressed", x: p.x, y: p.y, button: "left", clickCount: 1 }, sessionId);
      await send("Input.dispatchMouseEvent", { type: "mouseReleased", x: p.x, y: p.y, button: "left", clickCount: 1 }, sessionId);
    } else {
      console.error("элемент для клика не найден:", clickSelector);
    }
    await sleep(7000);
    for (let i = 0; i < 4; i++) {
      await send("Runtime.evaluate", { expression: "window.scrollTo(0, document.body.scrollHeight)" }, sessionId);
      await sleep(1200);
    }
  }

  const expr = jsFile
    ? await fs.readFile(jsFile, "utf-8")
    : `(() => ({
        title: document.title,
        url: location.href,
        text: document.body.innerText,
        links: [...document.querySelectorAll('a[href]')].map(a => ({ t: (a.innerText||'').trim().slice(0,100), h: a.href })).slice(0, 400)
      }))()`;

  let r;
  for (let attempt = 0; attempt < 3; attempt++) {
    try {
      r = await send(
        "Runtime.evaluate",
        { expression: expr, returnByValue: true, awaitPromise: true, userGesture: true },
        sessionId
      );
      break;
    } catch (e) {
      if (attempt === 2) throw e;
      await sleep(2000);
    }
  }
  const value = r?.result?.value ?? r?.result;
  await fs.writeFile(outFile, typeof value === "string" ? value : JSON.stringify(value, null, 2), "utf-8");
  console.log(`ok ${url} -> ${outFile}`);
} finally {
  if (targetId) {
    try {
      await send("Target.closeTarget", { targetId });
    } catch {}
  }
  ws.close();
  setTimeout(() => process.exit(0), 200);
}
