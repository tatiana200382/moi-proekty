(() => {
  const inp = [...document.querySelectorAll('input')].find(i => {
    const r = i.getBoundingClientRect();
    return r.width > 100 && r.top > 0 && r.top < 900;
  });
  if (!inp) return 'нет поля';
  const r = inp.getBoundingClientRect();
  return JSON.stringify({ x: Math.round(r.left + r.width/2), y: Math.round(r.top + r.height/2) });
})()
