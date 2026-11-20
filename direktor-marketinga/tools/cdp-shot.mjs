#!/usr/bin/env node
// Скриншот уже открытой вкладки (только чтение, без кликов и переходов).
// node cdp-shot.mjs <часть-url> <out.png>
import fs from "node:fs/promises";

const [, , urlPart, outFile] = process.argv;
const PORT = process.env.CDP_PORT || 9224;
const list = await (await fetch(`http://127.0.0.1:${PORT}/json/list`)).json();
const page = list.find((t) => t.type === "page" && t.url.includes(urlPart));
if (!page) {
  console.error("вкладка не найдена:", urlPart);
  process.exit(1);
}
const ws = new WebSocket(page.webSocketDebuggerUrl);
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
const send = (method, params = {}) =>
  new Promise((resolve, reject) => {
    const mid = ++id;
    pending.set(mid, { resolve, reject });
    ws.send(JSON.stringify({ id: mid, method, params }));
    setTimeout(() => pending.has(mid) && (pending.delete(mid), reject(new Error("таймаут"))), 30000);
  });
await send("Page.enable");
const r = await send("Page.captureScreenshot", { format: "png" });
await fs.writeFile(outFile, Buffer.from(r.data, "base64"));
console.log("снимок:", page.url, "->", outFile);
ws.close();
setTimeout(() => process.exit(0), 200);
