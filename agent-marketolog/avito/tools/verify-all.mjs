const PORT=9224;
const list=await (await fetch(`http://localhost:${PORT}/json/list`)).json();
const t=list.find(x=>x.type==='page'&&x.url.includes('avito.ru')) || list.find(x=>x.type==='page');
const ws=new WebSocket(t.webSocketDebuggerUrl);
await new Promise(r=>ws.addEventListener('open',r,{once:true}));
let id=0;const p=new Map();
ws.addEventListener('message',e=>{const m=JSON.parse(e.data); if(m.id&&p.has(m.id)){const q=p.get(m.id);p.delete(m.id);q(m.result);}});
const send=(m,params={})=>new Promise(res=>{const i=++id;p.set(i,res);ws.send(JSON.stringify({id:i,method:m,params}));});
const sleep=ms=>new Promise(r=>setTimeout(r,ms));
for (const d of ['1851307076','1851307478','1851307000','1851305517','1851296568']) {
  await send('Page.navigate',{url:'https://www.avito.ru/additem?draftId='+d});
  await sleep(11000);
  const r=await send('Runtime.evaluate',{expression:`(()=>{const s=document.querySelector('select[name="params[176306][]"]'); const v=document.querySelector('select[name="params[2836]"]'); const c=document.querySelector('select[name="params[112674]"]'); return JSON.stringify({d:location.href.split('=').pop(), comp:s?[...s.selectedOptions].length:0, vid:(v.selectedOptions[0]||{}).text||'', color:(c.selectedOptions[0]||{}).text||'', title:(document.querySelector('input[name="title"]')||{}).value});})()`,returnByValue:true});
  console.log(r.result.value);
}
ws.close();setTimeout(()=>process.exit(0),100);
