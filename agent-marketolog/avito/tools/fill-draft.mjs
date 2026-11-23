// Заполняет черновик: 5 фото, описание, вид «Продаю своё», цвет «Разноцветный».
// node fill-draft.mjs <draftId> <configPath>
import fs from 'node:fs';

const PORT = 9224;
const draft = process.argv[2];
const cfg = JSON.parse(fs.readFileSync(process.argv[3], 'utf8'))[draft];
if (!cfg) { console.log('нет конфига для', draft); process.exit(1); }

const list = await (await fetch(`http://localhost:${PORT}/json/list`)).json();
const tab = list.find(t => t.type === 'page' && t.url.includes('avito.ru')) || list.find(t => t.type === 'page');
const ws = new WebSocket(tab.webSocketDebuggerUrl);
await new Promise(r => ws.addEventListener('open', r, { once: true }));
let id = 0; const pend = new Map();
ws.addEventListener('message', e => { const m = JSON.parse(e.data); if (m.id && pend.has(m.id)) { const q = pend.get(m.id); pend.delete(m.id); q(m.result); } });
const send = (method, params = {}) => new Promise(res => { const i = ++id; pend.set(i, res); ws.send(JSON.stringify({ id: i, method, params })); });
const sleep = ms => new Promise(r => setTimeout(r, ms));

await send('DOM.enable');
await send('Page.navigate', { url: 'https://www.avito.ru/additem?draftId=' + draft });
await sleep(12000);

// 1) фото
const doc = await send('DOM.getDocument', { depth: -1 });
const q = await send('DOM.querySelector', { nodeId: doc.root.nodeId, selector: 'input[type=file]' });
let photos = 0;
if (q.nodeId) {
  await send('DOM.setFileInputFiles', { nodeId: q.nodeId, files: cfg.files });
  console.log('фото переданы:', cfg.files.length);
  await sleep(22000);
}
const cnt = await send('Runtime.evaluate', { expression: `document.querySelectorAll('[data-marker^="preview("]').length`, returnByValue: true });
photos = cnt.result.value;

// 2) описание
const desc = await send('Runtime.evaluate', { expression: `(()=>{
  const d=document.querySelector('div[contenteditable="true"], textarea[name="description"]');
  if(!d) return 'нет поля описания';
  d.focus();
  if(d.tagName==='TEXTAREA'){ const set=Object.getOwnPropertyDescriptor(window.HTMLTextAreaElement.prototype,'value').set; set.call(d, ${JSON.stringify(cfg.desc)}); d.dispatchEvent(new Event('input',{bubbles:true})); }
  else { const sel=window.getSelection(); const r=document.createRange(); r.selectNodeContents(d); sel.removeAllRanges(); sel.addRange(r); document.execCommand('delete',false,null); document.execCommand('insertText',false,${JSON.stringify(cfg.desc)}); }
  return (d.value||d.innerText||'').length;
})()`, returnByValue: true });

// 3) вид и цвет — кликами
async function clickAt(pt){ await send('Input.dispatchMouseEvent',{type:'mouseMoved',x:pt.x,y:pt.y}); await send('Input.dispatchMouseEvent',{type:'mousePressed',x:pt.x,y:pt.y,button:'left',clickCount:1}); await send('Input.dispatchMouseEvent',{type:'mouseReleased',x:pt.x,y:pt.y,button:'left',clickCount:1}); }
async function pick(marker, text){
  const box=await send('Runtime.evaluate',{expression:`(()=>{const f=document.querySelector('[data-marker="${marker}"]'); if(!f) return null; const kids=[...f.querySelectorAll('div')].filter(d=>d.getBoundingClientRect().height>40); const el=kids[kids.length-1]||f; el.scrollIntoView({block:'center'}); const b=el.getBoundingClientRect(); return JSON.stringify({x:Math.round(b.x+b.width/2), y:Math.round(b.y+b.height/2)});})()`,returnByValue:true});
  if(!box.result.value) return 'нет поля';
  await clickAt(JSON.parse(box.result.value)); await sleep(1300);
  const opt=await send('Runtime.evaluate',{expression:`(()=>{const el=[...document.querySelectorAll('*')].filter(e=>e.children.length===0 && (e.innerText||'').trim()===${JSON.stringify(text)} && e.getBoundingClientRect().height>0); const t=el.find(e=>e.getBoundingClientRect().y>0); if(!t) return null; t.scrollIntoView({block:'nearest'}); const b=t.getBoundingClientRect(); return JSON.stringify({x:Math.round(b.x+b.width/2), y:Math.round(b.y+b.height/2)});})()`,returnByValue:true});
  if(!opt.result.value) return 'нет опции';
  await clickAt(JSON.parse(opt.result.value)); await sleep(1200);
  return 'ок';
}
const v = await pick('params[2836]', 'Продаю своё');
const c = await pick('params[112674]', 'Разноцветный');

await sleep(2000);
const chk = await send('Runtime.evaluate', { expression: `(()=>{const v=document.querySelector('select[name="params[2836]"]'); const c=document.querySelector('select[name="params[112674]"]'); const d=document.querySelector('div[contenteditable="true"], textarea[name="description"]'); return JSON.stringify({photos:document.querySelectorAll('[data-marker^="preview("]').length, vid:(v.selectedOptions[0]||{}).text, color:(c.selectedOptions[0]||{}).text, descLen:(d?.value||d?.innerText||'').length});})()`, returnByValue: true });
console.log(draft, 'фото до/после:', photos, '|', v, c, '|', chk.result.value);
ws.close(); setTimeout(() => process.exit(0), 100);
