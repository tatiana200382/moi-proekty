(() => {
  const p = document.querySelector('[data-marker="price"]');
  const inp = p ? p.querySelector('input') : null;
  if (!inp) return 'нет поля';
  inp.scrollIntoView({block:'center'});
  inp.focus();
  inp.setSelectionRange(0, inp.value.length);
  const r = inp.getBoundingClientRect();
  return JSON.stringify({x:Math.round(r.left+r.width/2), y:Math.round(r.top+r.height/2), val:inp.value});
})()
