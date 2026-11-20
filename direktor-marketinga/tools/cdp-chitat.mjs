#!/usr/bin/env node
// ЧТЕНИЕ уже открытой вкладки: только document/окно, без кликов и переходов.
// Использование: node cdp-chitat.mjs <часть-url> <out.json> <js-файл>
import fs from "node:fs/promises";

const [, , urlPart, outFile, jsFile] = process.argv;
if (!urlPart || !outFile || !jsFile) {
  console.error("использование: node cdp-chitat.mjs <часть-url> <out.json> <js>");
  process.exit(1);
}
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
const expr = await fs.readFile(jsFile, "utf-8");
const r = await new Promise((resolve, reject) => {
  ws.addEventListener("message", (ev) => {
    const msg = JSON.parse(ev.data);
    if (msg.id === 1) (msg.error ? reject(new Error(JSON.stringify(msg.error))) : resolve(msg.result));
  });
  ws.send(
    JSON.stringify({
      id: 1,
      method: "Runtime.evaluate",
      params: { expression: expr, returnByValue: true, awaitPromise: true, userGesture: true },
    })
  );
  setTimeout(() => reject(new Error("таймаут")), 30000);
});
const value = r?.result?.value ?? r?.result;
await fs.writeFile(outFile, typeof value === "string" ? value : JSON.stringify(value, null, 2), "utf-8");
console.log("ok", page.url, "->", outFile);
ws.close();
setTimeout(() => process.exit(0), 200);
