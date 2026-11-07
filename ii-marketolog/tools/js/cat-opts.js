(() => {
  const out = [];
  document.querySelectorAll('button, [role=option], li, div').forEach(e => {
    const t = (e.innerText||'').trim();
    if (t.startsWith('Букеты · Растения') && t.length < 45) out.push({ tag:e.tagName, marker:e.getAttribute('data-marker')||'', cls:(e.className||'').toString().slice(0,30) });
  });
  return JSON.stringify(out.slice(0,6), null, 1);
})()
