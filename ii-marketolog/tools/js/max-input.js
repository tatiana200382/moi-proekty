(() => {
  const inputs = [...document.querySelectorAll('input')].map((i, idx) => ({
    idx, ph: i.placeholder || '', val: i.value || '', name: i.name || '', type: i.type
  })).filter(x => x.ph.toLowerCase().includes('max') || x.val.toLowerCase().includes('max') || (x.ph === '' && x.val === ''));
  const btns = [...document.querySelectorAll('button')].map(b => b.innerText.trim()).filter(t => t && t.length < 40);
  return JSON.stringify({ candidates: inputs.slice(0, 6), buttons: [...new Set(btns)].slice(0, 12) }, null, 1);
})()
