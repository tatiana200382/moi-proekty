(() => {
  const el=document.querySelector('[data-marker="sostav_buketa"]') || document.querySelector('[data-marker="sostav_buketa/select"]');
  if(!el) return 'нет';
  el.scrollIntoView({block:'center'});
  const r=el.getBoundingClientRect();
  return JSON.stringify({x:Math.round(r.left+r.width/2), y:Math.round(r.top+r.height/2), w:Math.round(r.width), h:Math.round(r.height)});
})()
