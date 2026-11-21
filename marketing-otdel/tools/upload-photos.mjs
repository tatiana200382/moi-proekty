// upload-photos.mjs — загрузить файлы в первое поле input[type=file] на странице.
// node tools/upload-photos.mjs "<url-substring>" <файл1> [файл2 ...]
import path from "node:path";

const [target, ...files] = process.argv.slice(2);
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

const r = await send("Runtime.evaluate", { expression: "document.querySelector('input[type=file]')" });
if (!r.result || !r.result.objectId) {
  console.error("нет поля загрузки файлов");
  process.exit(1);
}
const abs = files.map((f) => path.resolve(f));
await send("DOM.setFileInputFiles", { objectId: r.result.objectId, files: abs });
console.log("загружено файлов:", abs.length);
ws.close();
process.exit(0);
