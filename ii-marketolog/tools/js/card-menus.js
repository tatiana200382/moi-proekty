(() => {
  const out = [];
  document.querySelectorAll('[aria-label]').forEach(e => {
    const a = e.getAttribute('aria-label') || '';
    if (/ещё|меню|действ|опци/i.test(a)) {
      const r = e.getBoundingClientRect();
      out.push({ a, tag: e.tagName, y: Math.round(r.top), w: Math.round(r.width) });
    }
  });
  return JSON.stringify(out.slice(0, 8), null, 1);
})()
