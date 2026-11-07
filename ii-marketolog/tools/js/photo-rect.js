(() => {
  const img = [...document.querySelectorAll('img')].filter(i => i.width > 100)[0];
  if (!img) return 'нет';
  const r = img.getBoundingClientRect();
  return JSON.stringify({x: Math.round(r.left + r.width/2), y: Math.round(r.top + r.height/2)});
})()
