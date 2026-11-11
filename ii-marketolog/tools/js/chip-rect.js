(() => {
  const chips=[...document.querySelectorAll('[data-marker="sostav_buketa/select-text"] *')];
  const texts=[...document.querySelectorAll('*')].filter(e=>e.children.length===0 && e.textContent.trim()==='Альстромерии');
  const el=texts[0];
  if(!el) return 'нет чипа';
  const r=el.getBoundingClientRect();
  return JSON.stringify({x:Math.round(r.right+16), y:Math.round(r.top+r.height/2)});
})()
