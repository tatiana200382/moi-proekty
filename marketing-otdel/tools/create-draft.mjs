// create-draft.mjs — создать черновик объявления в категории «Растения → Букеты».
// node tools/create-draft.mjs "<заголовок>" "<фото.jpg>"
import path from "node:path";

const [title, photo] = process.argv.slice(2);
if (!title || !photo) {
  console.error('usage: node tools/create-draft.mjs "<заголовок>" "<фото>"');
  process.exit(2);
}

const list = await (await fetch("http://127.0.0.1:9224/json/list")).json();
let page = list.filter((t) => t.type === "page")[0];
if (!page) {
  console.error("нет вкладок Chrome");
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
const sleep = (ms) => new Promise((r) => setTimeout(r, ms));
const js = async (expression) => (await send("Runtime.evaluate", { expression, returnByValue: true })).result?.value;

const clickText = (text) =>
  js(`(() => {
    const els = [...document.querySelectorAll('*')].filter(e => e.children.length === 0 && (e.textContent || '').trim() === ${JSON.stringify(text)});
    if (!els.length) return 'нет: ' + ${JSON.stringify(text)};
    (els[els.length - 1].closest('a,button,div,li') || els[els.length - 1]).click();
    return 'ok: ' + ${JSON.stringify(text)};
  })()`);

console.log("→ открываю форму");
await send("Page.navigate", { url: "https://www.avito.ru/additem" });
await sleep(9000);

console.log("→ категория");
console.log(await clickText("Другая категория"));
await sleep(2500);
console.log(await clickText("Для дома и дачи"));
await sleep(3500);

console.log("→ заголовок");
console.log(
  await js(`(() => {
    const inp = document.querySelector('input');
    if (!inp) return 'нет поля';
    Object.getOwnPropertyDescriptor(window.HTMLInputElement.prototype, 'value').set.call(inp, ${JSON.stringify(title)});
    inp.dispatchEvent(new Event('input', { bubbles: true }));
    return 'title:' + inp.value.length;
  })()`)
);
await sleep(3000);
console.log(await clickText("Букеты · Растения · Для дома и дачи"));
await sleep(3000);

console.log("→ вид объявления");
for (const type of ["mousePressed", "mouseReleased"]) {
  await send("Input.dispatchMouseEvent", { type, x: 295, y: 449, button: "left", clickCount: 1 });
}
await sleep(1200);
await send("Input.insertText", { text: "Товар приобретён на продажу" });
await sleep(2500);
console.log(await clickText("Товар приобретён на продажу"));
await sleep(2000);

console.log("→ фото");
const r = await send("Runtime.evaluate", { expression: "document.querySelector('input[type=file]')" });
if (r.result?.objectId) {
  await send("DOM.setFileInputFiles", { objectId: r.result.objectId, files: [path.resolve(photo)] });
  console.log("фото загружено");
} else {
  console.log("нет поля файла");
}
await sleep(4000);

const url = await js("location.href");
console.log("итог:", url);
ws.close();
process.exit(0);
