#!/usr/bin/env node
// Открыть URL в своей вкладке, снять скриншот, закрыть. Только чтение.
// node cdp-snimok-png.mjs <url> <out.png> [waitMs]
import fs from "node:fs/promises";
const [, , url, outFile, waitArg] = process.argv;
const PORT = process.env.CDP_PORT || 9224;
const wait = Number(waitArg) || 9000;
const sleep = (ms) => new Promise((r) => setTimeout(r, ms));
const ver = await (await fetch(`http://127.0.0.1:${PORT}/json/version`)).json();
const ws = new WebSocket(ver.webSocketDebuggerUrl);
await new Promise((res, rej) => { ws.addEventListener("open", res, { once: true }); ws.addEventListener("error", rej, { once: true }); });
let id = 0; const pending = new Map();
ws.addEventListener("message", (ev) => { const m = JSON.parse(ev.data); if (m.id && pending.has(m.id)) { const { resolve, reject } = pending.get(m.id); pending.delete(m.id); m.error ? reject(new Error(JSON.stringify(m.error))) : resolve(m.result); } });
const send = (method, params = {}, sessionId) => new Promise((resolve, reject) => { const mid = ++id; pending.set(mid, { resolve, reject }); const msg = { id: mid, method, params }; if (sessionId) msg.sessionId = sessionId; ws.send(JSON.stringify(msg)); setTimeout(() => pending.has(mid) && (pending.delete(mid), reject(new Error("таймаут " + method))), 60000); });
const { targetId } = await send("Target.createTarget", { url: "about:blank" });
const { sessionId } = await send("Target.attachToTarget", { targetId, flatten: true });
await send("Page.enable", {}, sessionId);
await send("Page.navigate", { url }, sessionId);
await sleep(wait);
const r = await send("Page.captureScreenshot", { format: "png" }, sessionId);
await fs.writeFile(outFile, Buffer.from(r.data, "base64"));
console.log("png:", url, "->", outFile);
await send("Target.closeTarget", { targetId });
ws.close(); setTimeout(() => process.exit(0), 200);
