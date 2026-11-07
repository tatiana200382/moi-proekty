(() => {
  const opts = [...document.querySelectorAll('*')].filter(e => e.children.length===0 && /Белышева/.test(e.textContent||'') && (e.textContent||'').length < 80);
  return JSON.stringify(opts.slice(0,5).map(o => ({t:o.textContent.trim(), tag:o.tagName, marker:(o.closest('[data-marker]')||{}).getAttribute?.('data-marker')||''})), null, 1);
})()
