// set-description.mjs — заполнить поле описания на странице редактирования Авито.
// node tools/set-description.mjs "<url-substring>" <file-with-text>
import fs from "node:fs/promises";

const [target, file] = process.argv.slice(2);
const text = await fs.readFile(file, "utf8");
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
    setTimeout(() => pending.has(i) && (pending.delete(i), reject(new Error("timeout " + method))), 30000);
  });

const expr = `(() => {
  const area = document.querySelector('[contenteditable=true]');
  if (!area) return 'нет поля';
  area.focus();
  document.execCommand('selectAll', false, null);
  document.execCommand('insertText', false, ${JSON.stringify(text)});
  return 'ok:' + (area.innerText || '').length;
})()`;

const r = await send("Runtime.evaluate", { expression: expr, returnByValue: true });
console.log(r.result?.value ?? JSON.stringify(r));
ws.close();
process.exit(0);
