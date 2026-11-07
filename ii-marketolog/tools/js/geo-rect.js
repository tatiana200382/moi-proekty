(() => {
  const el = document.querySelector('[data-marker="geo/field/suggest"]');
  if (!el) return 'нет поля адреса';
  el.scrollIntoView({block:'center'});
  const inp = el.querySelector('input') || el;
  const r = inp.getBoundingClientRect();
  return JSON.stringify({x:Math.round(r.left+r.width/2), y:Math.round(r.top+r.height/2), tag:inp.tagName});
})()
