(() => {
  const imgs = [...document.querySelectorAll('img')].filter(i => i.width > 60);
  const info = imgs.slice(0, 8).map((i, idx) => {
    let p = i, btns = [];
    for (let k=0;k<4&&p;k++){ p = p.parentElement; if (p) btns = btns.concat([...p.querySelectorAll('button')].map(b => b.getAttribute('aria-label')||b.innerText.trim()).filter(Boolean)); }
    return { idx, src: (i.src||'').slice(-24), btns: [...new Set(btns)].slice(0,4) };
  });
  return JSON.stringify(info, null, 1);
})()
