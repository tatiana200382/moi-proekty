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

async function clickPoint(pt){
  await send('Input.dispatchMouseEvent',{type:'mouseMoved',x:pt.x,y:pt.y});
  await send('Input.dispatchMouseEvent',{type:'mousePressed',x:pt.x,y:pt.y,button:'left',clickCount:1});
  await send('Input.dispatchMouseEvent',{type:'mouseReleased',x:pt.x,y:pt.y,button:'left',clickCount:1});
}
async function pick(marker, text){
  const box=await send('Runtime.evaluate',{expression:`(()=>{const f=document.querySelector('[data-marker="${marker}"]'); if(!f) return null; const kids=[...f.querySelectorAll('div')].filter(d=>d.getBoundingClientRect().height>40); const el=kids[kids.length-1]||f; el.scrollIntoView({block:'center'}); const b=el.getBoundingClientRect(); return JSON.stringify({x:Math.round(b.x+b.width/2), y:Math.round(b.y+b.height/2)});})()`,returnByValue:true});
  if(!box.result.value) return 'нет поля';
  await clickPoint(JSON.parse(box.result.value));
  await sleep(1300);
  const opt=await send('Runtime.evaluate',{expression:`(()=>{const el=[...document.querySelectorAll('*')].filter(e=>e.children.length===0 && (e.innerText||'').trim()===${JSON.stringify(text)} && e.getBoundingClientRect().height>0); const t=el.find(e=>e.getBoundingClientRect().y>0); if(!t) return null; t.scrollIntoView({block:'nearest'}); const b=t.getBoundingClientRect(); return JSON.stringify({x:Math.round(b.x+b.width/2), y:Math.round(b.y+b.height/2)});})()`,returnByValue:true});
  if(!opt.result.value) return 'нет опции';
  await clickPoint(JSON.parse(opt.result.value));
  await sleep(1200);
  return 'ок';
}

await send('Page.navigate',{url:'https://www.avito.ru/additem?draftId='+draft});
await sleep(12000);
const a = await pick('params[2836]', 'Продаю своё');
const b = await pick('params[112674]', 'Разноцветный');
const chk=await send('Runtime.evaluate',{expression:`(()=>{const v=document.querySelector('select[name="params[2836]"]'); const c=document.querySelector('select[name="params[112674]"]'); return JSON.stringify({vid:(v.selectedOptions[0]||{}).text, color:(c.selectedOptions[0]||{}).text});})()`,returnByValue:true});
console.log(draft, a, b, chk.result.value);
ws.close();setTimeout(()=>process.exit(0),100);
