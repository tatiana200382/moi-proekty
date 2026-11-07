(() => {
  const lab = [...document.querySelectorAll('*')].find(e => e.children.length===0 && (e.textContent||'').trim()==='Состав букета');
  if (!lab) return 'нет метки';
  const block = lab.parentElement;
  const inp = block.querySelector('input');
  if (inp) { inp.scrollIntoView({block:'center'}); inp.focus(); const r=inp.getBoundingClientRect(); return JSON.stringify({type:'input', x:Math.round(r.left+r.width/2), y:Math.round(r.top+r.height/2)}); }
  block.scrollIntoView({block:'center'});
  const r = block.getBoundingClientRect();
  return JSON.stringify({type:'block', x:Math.round(r.left+r.width/2), y:Math.round(r.bottom-20)});
})()
