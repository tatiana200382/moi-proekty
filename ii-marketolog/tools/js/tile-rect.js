(() => {
  const el = [...document.querySelectorAll('*')].find(e => (e.textContent||'').trim().endsWith('Новая история') && (e.textContent||'').length < 40);
  if (!el) return 'нет';
  let p = el; for (let i=0;i<3 && p;i++){ const r=p.getBoundingClientRect(); if (r.width>100 && r.height>100) return JSON.stringify({x:Math.round(r.left+r.width/2), y:Math.round(r.top+r.height/2), w:Math.round(r.width), h:Math.round(r.height)}); p=p.parentElement; }
  return 'не нашёл плитку';
})()
