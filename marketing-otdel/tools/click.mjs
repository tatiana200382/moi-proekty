// click.mjs — клик по координатам скриншота в вкладке, найденной по подстроке URL.
// node tools/click.mjs "<url-substring>" <x> <y> [<x2> <y2> ...]
// Координаты — в пикселях скриншота (CDP пересчитывает в CSS с учётом масштаба).
import fs from "node:fs/promises";

const args = process.argv.slice(2);
const target = args[0];
const points = [];
for (let i = 1; i + 1 < args.length; i += 2) points.push([Number(args[i]), Number(args[i + 1])]);

const list = await (await fetch("http://127.0.0.1:9224/json/list")).json();
const page = list.filter((t) => t.type === "page").find((t) => t.url.includes(target));
if (!page) {
  console.error("нет вкладки с", target);
  process.exit(2);
}

const ws = new WebSocket(page.webSocketDebuggerUrl);
await new Promise((r, j) => {
  ws.addEventListener("open", r, { once: true });
  ws.addEventListener("error", j, { once: true });
});
let id = 0;
const pending = new Map();
ws.addEventListener("message", (ev) => {
  const m = JSON.parse(ev.data);
  if (m.id && pending.has(m.id)) {
    const p = pending.get(m.id);
    pending.delete(m.id);
    m.error ? p.reject(new Error(JSON.stringify(m.error))) : p.resolve(m.result);
  }
});
const send = (method, params = {}) =>
  new Promise((resolve, reject) => {
    const i = ++id;
    pending.set(i, { resolve, reject });
    ws.send(JSON.stringify({ id: i, method, params }));
    setTimeout(() => pending.has(i) && (pending.delete(i), reject(new Error("timeout " + method))), 20000);
  });

await send("Page.enable");
await send("Page.bringToFront");
const metrics = await send("Page.getLayoutMetrics");
const vp = metrics.cssLayoutViewport;
const shot = await send("Page.captureScreenshot", { format: "png" });
const buf = Buffer.from(shot.data, "base64");
const pngW = buf.readUInt32BE(16);
const scale = pngW / vp.clientWidth;

for (const [x, y] of points) {
  const cx = x / scale;
  const cy = y / scale;
  await send("Input.dispatchMouseEvent", { type: "mouseMoved", x: cx, y: cy });
  await send("Input.dispatchMouseEvent", { type: "mousePressed", x: cx, y: cy, button: "left", clickCount: 1 });
  await send("Input.dispatchMouseEvent", { type: "mouseReleased", x: cx, y: cy, button: "left", clickCount: 1 });
  console.log("click", Math.round(cx), Math.round(cy));
  await new Promise((r) => setTimeout(r, 900));
}
ws.close();
process.exit(0);
