const PORT=9224;
const list=await (await fetch(`http://localhost:${PORT}/json/list`)).json();
const t=list.find(x=>x.type==='page'&&x.url.includes('avito.ru')) || list.find(x=>x.type==='page');
const ws=new WebSocket(t.webSocketDebuggerUrl);
await new Promise(r=>ws.addEventListener('open',r,{once:true}));
let id=0;const p=new Map();
ws.addEventListener('message',e=>{const m=JSON.parse(e.data); if(m.id&&p.has(m.id)){const q=p.get(m.id);p.delete(m.id);q(m.result);}});
const send=(m,params={})=>new Promise(res=>{const i=++id;p.set(i,res);ws.send(JSON.stringify({id:i,method:m,params}));});
const sleep=ms=>new Promise(r=>setTimeout(r,ms));
const draft=process.argv[2];
const all = ["Альстромерии","Амариллисы","Анемоны","Астильба","Астранции","Астры","Васильки","Гвоздики","Георгины","Герберы","Гиацинты","Гипсофилы","Гладиолусы","Гортензии","Дельфиниум","Диантусы","Другие","Ирисы","Каллы","Колокольчики","Лаванда","Ландыши","Лизиантусы","Лилии","Матрикарии","Маттиола","Мимозы","Нарциссы","Незабудки","Орхидеи","Пионы","Подснежники","Подсолнухи","Полевые","Ранункулюсы","Розы","Ромашки","Сирень","Тюльпаны"];
async function state(){const r=await send('Runtime.evaluate',{expression:`(()=>{const s=document.querySelector('select[name="params[176306][]"]'); if(!s) return '{}'; return JSON.stringify({names:[...s.selectedOptions].map(o=>o.text)});})()`,returnByValue:true}); return JSON.parse(r.result.value||'{}').names||[];}
async function fieldXY(){const r=await send('Runtime.evaluate',{expression:`(()=>{const f=document.querySelector('[data-marker="params[176306][]"]'); if(!f) return null; f.scrollIntoView({block:'center'}); const b=f.getBoundingClientRect(); return JSON.stringify({x:Math.round(b.x+b.width/2), y:Math.round(b.y+b.height/2)});})()`,returnByValue:true}); return r.result.value?JSON.parse(r.result.value):null;}
async function findXY(name){const r=await send('Runtime.evaluate',{expression:`(()=>{const el=[...document.querySelectorAll('*')].find(e=>e.children.length===0 && (e.innerText||'').trim()===${JSON.stringify(name)} && e.getBoundingClientRect().height>0); if(!el) return null; el.scrollIntoView({block:'center'}); const b=el.getBoundingClientRect(); return JSON.stringify({x:Math.round(b.x+b.width/2), y:Math.round(b.y+b.height/2)});})()`,returnByValue:true}); return r.result.value?JSON.parse(r.result.value):null;}
async function clickAt(pt){await send('Input.dispatchMouseEvent',{type:'mouseMoved',x:pt.x,y:pt.y});await send('Input.dispatchMouseEvent',{type:'mousePressed',x:pt.x,y:pt.y,button:'left',clickCount:1});await send('Input.dispatchMouseEvent',{type:'mouseReleased',x:pt.x,y:pt.y,button:'left',clickCount:1});}
await send('Page.navigate',{url:'https://www.avito.ru/additem?draftId='+draft});
await sleep(12000);
await send('Runtime.evaluate',{expression:`(()=>{const d=Object.getOwnPropertyDescriptor(window.HTMLSelectElement.prototype,'value').set; const v=document.querySelector('select[name="params[2836]"]'); if(v){const o=[...v.options].find(x=>/Продаю своё/.test(x.text)); if(o){d.call(v,o.value); v.dispatchEvent(new Event('change',{bubbles:true}));}} const c=document.querySelector('select[name="params[112674]"]'); if(c){const o=[...c.options].find(x=>/разноцвет/i.test(x.text)); if(o){d.call(c,o.value); c.dispatchEvent(new Event('change',{bubbles:true}));}} return 1;})()`,returnByValue:true});
await sleep(1500);
for (let pass=0; pass<5; pass++){
  const sel=await state();
  const todo=all.filter(n=>!sel.includes(n));
  if(!todo.length) break;
  for (const nm of todo){
    let pt=await findXY(nm);
    if(!pt){const f=await fieldXY(); if(!f) break; await clickAt(f); await sleep(800); pt=await findXY(nm);}
    if(!pt) continue;
    await clickAt(pt); await sleep(280);
  }
}
const sel=await state();
console.log(draft, 'выбрано цветов:', sel.length);
ws.close();setTimeout(()=>process.exit(0),100);
