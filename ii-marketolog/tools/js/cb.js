(() => {
  const out = [];
  [...document.querySelectorAll('input[type=checkbox]')].forEach((c, i) => {
    const r = c.getBoundingClientRect();
    const lbl = (c.closest('label') || c.parentElement || {}).innerText || '';
    out.push({ i, y: Math.round(r.top), w: Math.round(r.width), label: lbl.replace(/\n+/g, ' ').slice(0, 40), checked: c.checked });
  });
  return JSON.stringify(out.slice(0, 10), null, 1);
})()
