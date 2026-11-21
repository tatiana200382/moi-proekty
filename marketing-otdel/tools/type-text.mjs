// type-text.mjs — ввод текста в сфокусированное поле и, по желанию, Enter.
// node tools/type-text.mjs "<url-substring>" "<текст>" [--enter]
import fs from "node:fs/promises";

const [target, text, flag] = process.argv.slice(2);
const list = await (await fetch("http://127.0.0.1:9224/json/list")).json();
const page = list.filter((t) => t.type === "page").find((t) => t.url.includes(target));
if (!page) {
  console.error("нет вкладки с", target);
  process.exit(2);
}
const ws = new WebSocket(page.webSocketDebuggerUrl);
await new Promise((r) => ws.addEventListener("open", r, { once: true }));
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
    setTimeout(() => pending.has(i) && (pending.delete(i), reject(new Error("timeout " + method))), 15000);
  });

await send("Input.insertText", { text });
if (flag === "--enter") {
  await new Promise((r) => setTimeout(r, 700));
  await send("Input.dispatchKeyEvent", { type: "keyDown", key: "Enter", windowsVirtualKeyCode: 13, nativeVirtualKeyCode: 36 });
  await send("Input.dispatchKeyEvent", { type: "keyUp", key: "Enter", windowsVirtualKeyCode: 13, nativeVirtualKeyCode: 36 });
}
console.log("введено");
ws.close();
process.exit(0);
