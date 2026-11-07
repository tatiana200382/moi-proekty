(() => {
  const out = [];
  document.querySelectorAll('button, [role=button]').forEach(b => {
    const t = (b.innerText||'').trim();
    const a = b.getAttribute('aria-label')||'';
    if (!t && a) out.push({ aria: a });
  });
  return JSON.stringify(out.slice(0,10), null, 1);
})()
