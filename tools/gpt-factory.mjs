// Отправляет задачу в ChatGPT и сохраняет ответ в файл.
// Использование: node tools/gpt-factory.mjs <файл-задачи> <файл-ответа>
import fs from 'node:fs';
import path from 'node:path';

const [taskPath, outPath] = process.argv.slice(2);
if (!taskPath || !outPath) { console.error('usage: node tools/gpt-factory.mjs <task> <out>'); process.exit(2); }
const PORT = 9224;
const task = fs.readFileSync(taskPath, 'utf8');

const list = await (await fetch(`http://localhost:${PORT}/json/list`)).json();
let t = list.filter(x => x.type === 'page' && x.url.includes('chatgpt.com'))[0];
if (!t) { console.error('нет вкладки ChatGPT'); process.exit(2); }
const ws = new WebSocket(t.webSocketDebuggerUrl);
await new Promise(r => ws.addEventListener('open', r, { once: true }));
let id = 0; const p = new Map();
ws.addEventListener('message', e => { const m = JSON.parse(e.data); if (m.id && p.has(m.id)) { const q = p.get(m.id); p.delete(m.id); q(m.result); } });
const send = (method, params = {}) => new Promise(res => { const i = ++id; p.set(i, res); ws.send(JSON.stringify({ id: i, method, params })); });
const sleep = (ms) => new Promise(r => setTimeout(r, ms));

const prompt = `Ты контент-завод Silver Song Flowers. Прочитай задачу и ответь по формату из pravila-dlya-fabriki.md: сразу материал, без вступлений, в конце "Что проверить" и "Открытые вопросы". Не выдумывай факты.\n\n--- ЗАДАЧА ---\n${task}`;

await send('Page.navigate', { url: 'https://chatgpt.com/' });
await sleep(7000);
await send('Runtime.evaluate', { expression: `(() => { const el=document.querySelector('.ProseMirror'); if(!el) return 'нет поля'; el.focus(); return 'ok'; })()`, returnByValue: true });
await sleep(500);
await send('Input.insertText', { text: prompt });
await sleep(1200);
await send('Input.dispatchKeyEvent', { type: 'keyDown', key: 'Enter', code: 'Enter', windowsVirtualKeyCode: 13, nativeVirtualKeyCode: 36 });
await send('Input.dispatchKeyEvent', { type: 'keyUp', key: 'Enter', code: 'Enter', windowsVirtualKeyCode: 13, nativeVirtualKeyCode: 36 });
console.log('задача отправлена, ждём ответ…');
await sleep(45000);

const r = await send('Runtime.evaluate', { expression: `(() => {
  const nodes = [...document.querySelectorAll('[data-message-author-role="assistant"]')];
  const last = nodes[nodes.length - 1];
  return last ? last.innerText : '';
})()`, returnByValue: true });
const answer = (r.result.value || '').trim();
if (!answer) { console.error('ответ не получен'); process.exit(1); }
fs.mkdirSync(path.dirname(outPath), { recursive: true });
fs.writeFileSync(outPath, `# Ответ контент-завода\n\nЗадача: ${taskPath}\nИсточник: ChatGPT\n\n${answer}\n`, 'utf8');
console.log('сохранено:', outPath, answer.length, 'знаков');
ws.close(); setTimeout(() => process.exit(0), 100);
