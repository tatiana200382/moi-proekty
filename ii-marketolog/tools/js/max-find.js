(() => {
  const out = [];
  [...document.querySelectorAll('input')].forEach((i, idx) => {
    const r = i.getBoundingClientRect();
    if (r.width > 50) {
      let p = i, label = '';
      for (let k = 0; k < 4 && p; k++) { p = p.parentElement; if (p) { const tx = (p.innerText || '').trim(); if (tx) { label = tx.replace(/\n+/g, ' | ').slice(0, 60); break; } } }
      out.push({ idx, y: Math.round(r.top), label });
    }
  });
  return JSON.stringify(out.slice(0, 12), null, 1);
})()
