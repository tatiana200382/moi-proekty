(() => {
  const out = [];
  document.querySelectorAll('*').forEach(e => {
    const t = (e.textContent||'').trim();
    if (t === 'Другая категория' && e.children.length <= 1) {
      let p = e;
      for (let i=0;i<4&&p;i++){ out.push({ tag:p.tagName, cls:(p.className||'').toString().slice(0,40), role:p.getAttribute&&p.getAttribute('role')||'' }); p=p.parentElement; }
    }
  });
  return JSON.stringify(out.slice(0,10), null, 1);
})()
