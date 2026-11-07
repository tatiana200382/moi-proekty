(() => {
  const el = [...document.querySelectorAll('*')].find(e => e.children.length===0 && (e.textContent||'').trim()==='Укажите значение параметра');
  if (!el) return 'нет';
  el.scrollIntoView({block:'center'});
  const r = el.getBoundingClientRect();
  return JSON.stringify({x:Math.round(r.left+60), y:Math.round(r.top+r.height/2)});
})()
