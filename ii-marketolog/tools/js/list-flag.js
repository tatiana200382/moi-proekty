(() => {
  const els = [...document.querySelectorAll('*')].filter(e => e.children.length===0 && e.textContent.trim()==='Обновить данные');
  const info = els.map(e => {
    let p = e, chain=[];
    for (let i=0;i<4&&p;i++){ p=p.parentElement; if(p) chain.push((p.innerText||'').replace(/\n+/g,' | ').slice(0,80)); }
    return {tag:e.tagName, cls:(e.className||'').toString().slice(0,50), title:e.title||'', chain:chain.slice(0,2)};
  });
  return JSON.stringify({count: els.length, info}, null, 1);
})()
