(() => {
  const t = document.body.innerText.split('\n').map(s=>s.trim()).filter(Boolean);
  const start = t.findIndex(l => /^Активные/.test(l));
  return JSON.stringify(t.slice(start, start + 45), null, 1);
})()
