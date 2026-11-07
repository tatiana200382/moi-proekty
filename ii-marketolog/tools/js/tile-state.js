(() => {
  const el = [...document.querySelectorAll('*')].find(e => (e.textContent||'').trim() === '+Новая история' || (e.textContent||'').trim() === 'Новая история');
  if (!el) return 'нет элемента';
  let p = el.before ? el : el;
  const info = [];
  let q = el;
  for (let i=0;i<4 && q;i++){ info.push({tag:q.tagName, cls:(q.className||'').toString().slice(0,50), aria:q.getAttribute('aria-disabled')||q.getAttribute('disabled')||''}); q=q.parentElement; }
  return JSON.stringify(info, null, 1);
})()
