(() => {
  const imgs = [...document.querySelectorAll('img')].map(i=>i.src).filter(s=>s.includes('vkuserphoto'));
  const uniq = [...new Set(imgs)];
  const txt = document.body.innerText.replace(/\n{2,}/g,'\n');
  return JSON.stringify({
    photos: uniq.length,
    sample: uniq.slice(0,3),
    ctx: txt.split('\n').filter(l=>/альбом|фото|Фотограф/i.test(l)).slice(0,10)
  }, null, 1);
})()
