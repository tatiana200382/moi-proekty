(() => {
  const el = [...document.querySelectorAll('*')].find(e => (e.textContent||'').trim() === 'Быстрые ответы');
  if (!el) return 'нет';
  let p = el;
  for (let i=0;i<4 && p;i++){ const r=p.getBoundingClientRect(); if (r.width>200 && r.height>50) { p.scrollIntoView({block:'center'}); const r2=p.getBoundingClientRect(); return JSON.stringify({x:Math.round(r2.left+r2.width/2), y:Math.round(r2.top+r2.height/2), tag:p.tagName}); } p=p.parentElement; }
  return 'не нашёл карточку';
})()
