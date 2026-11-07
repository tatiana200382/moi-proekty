(() => {
  const inputs = [...document.querySelectorAll('input,textarea')].map((i, idx) => {
    const r = i.getBoundingClientRect();
    return { idx, tag:i.tagName, type:i.type, ph:i.placeholder||'', val:(i.value||'').slice(0,30), y:Math.round(r.top), w:Math.round(r.width) };
  }).filter(x => x.w > 60);
  return JSON.stringify({ inputs: inputs.slice(0, 12), files: document.querySelectorAll('input[type=file]').length }, null, 1);
})()
