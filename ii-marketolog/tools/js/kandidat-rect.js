(() => {
  const el = [...document.querySelectorAll('*')].find(e => (e.textContent||'').trim().startsWith('Кандидатам на вакансию') && (e.textContent||'').length < 300);
  if (!el) return 'нет';
  el.scrollIntoView({block:'center'});
  const r = el.getBoundingClientRect();
  return JSON.stringify({x:Math.round(r.left+r.width/2), y:Math.round(r.top+20)});
})()
