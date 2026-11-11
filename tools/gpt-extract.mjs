// Забирает последний ответ ассистента из открытого чата ChatGPT и сохраняет в файл.
// Использование: node tools/gpt-extract.mjs <файл-ответа> [файл-задачи]
import fs from 'node:fs';
import path from 'node:path';
const [outPath, taskPath = ''] = process.argv.slice(2);
if (!outPath) { console.error('usage: node tools/gpt-extract.mjs <out> [task]'); process.exit(2); }
const PORT = 9224;
const list = await (await fetch(`http://localhost:${PORT}/json/list`)).json();
const t = list.filter(x => x.type === 'page' && x.url.includes('chatgpt.com/c/')).pop();
if (!t) { console.error('нет открытого чата ChatGPT'); process.exit(2); }
const ws = new WebSocket(t.webSocketDebuggerUrl);
await new Promise(r => ws.addEventListener('open', r, { once: true }));
let id = 0; const p = new Map();
ws.addEventListener('message', e => { const m = JSON.parse(e.data); if (m.id && p.has(m.id)) { const q = p.get(m.id); p.delete(m.id); q(m.result); } });
const send = (method, params = {}) => new Promise(res => { const i = ++id; p.set(i, res); ws.send(JSON.stringify({ id: i, method, params })); });
const r = await send('Runtime.evaluate', { expression: 'document.body.innerText', returnByValue: true });
const text = r.result.value || '';
const marker = 'ChatGPT сказал:';
let idx = text.lastIndexOf(marker);
let answer = '';
if (idx !== -1) {
  answer = text.slice(idx + marker.length);
  const stop = answer.indexOf('ChatGPT может допускать ошибки');
  if (stop !== -1) answer = answer.slice(0, stop);
} else {
  answer = text;
}
answer = answer.replace(/\s+Последний ответ[\s\S]*$/, '').trim();
if (!answer) { console.error('ответ не найден'); process.exit(1); }
fs.mkdirSync(path.dirname(outPath), { recursive: true });
const head = taskPath ? `Задача: ${taskPath}\n` : '';
fs.writeFileSync(outPath, `# Ответ контент-завода\n\n${head}Источник: ChatGPT\n\n${answer}\n`, 'utf8');
console.log('сохранено:', outPath, answer.length, 'знаков');
ws.close(); setTimeout(() => process.exit(0), 100);
