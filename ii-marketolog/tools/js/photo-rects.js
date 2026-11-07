(() => {
  const imgs=[...document.querySelectorAll('img')].filter(i=>i.width>80 && /avito|img/.test(i.src) && i.getBoundingClientRect().top>0);
  return JSON.stringify(imgs.slice(0,5).map(i=>{const r=i.getBoundingClientRect(); return {x:Math.round(r.right-8), y:Math.round(r.top+8), w:Math.round(r.width)};}), null, 1);
})()
