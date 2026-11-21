// insert-description.mjs — вставить текст в редактор описания «по-настоящему» (CDP Input).
// node tools/insert-description.mjs "<url-substring>" <file>
import fs from "node:fs/promises";

const [target, file] = process.argv.slice(2);
const text = (await fs.readFile(file, "utf8")).trim();
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
    setTimeout(() => pending.has(i) && (pending.delete(i), reject(new Error("timeout " + method))), 20000);
  });

// 1. Фокус и выделение всего текста в редакторе.
await send("Runtime.evaluate", {
  expression: `(() => { const a = document.querySelector('[contenteditable=true]'); if (!a) return 'нет'; a.focus(); document.execCommand('selectAll', false, null); return 'focused'; })()`,
  returnByValue: true,
});
// 2. Удалить выделенное.
await send("Input.dispatchKeyEvent", { type: "keyDown", key: "Backspace", windowsVirtualKeyCode: 8, nativeVirtualKeyCode: 51 });
await send("Input.dispatchKeyEvent", { type: "keyUp", key: "Backspace", windowsVirtualKeyCode: 8, nativeVirtualKeyCode: 51 });
await new Promise((r) => setTimeout(r, 500));
// 3. Вставить текст как при наборе.
await send("Input.insertText", { text });
await new Promise((r) => setTimeout(r, 800));
const r = await send("Runtime.evaluate", {
  expression: `(() => { const a = document.querySelector('[contenteditable=true]'); return a ? a.innerText.length : -1; })()`,
  returnByValue: true,
});
console.log("длина описания:", r.result?.value);
ws.close();
process.exit(0);
