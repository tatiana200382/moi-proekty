(() => {
  const rows = [...document.querySelectorAll('a, [role=link], [data-marker]')].map(a => ({tag:a.tagName, marker:a.getAttribute('data-marker')||'', href:a.href||'', text:(a.innerText||'').trim().replace(/\n+/g,' ').slice(0,40)}));
  return JSON.stringify(rows.filter(r => /Другая|категор/i.test(r.text || '')).slice(0,8), null, 1);
})()
