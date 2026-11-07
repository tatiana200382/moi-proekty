(() => {
  const links = [...document.querySelectorAll('a[href*="album"]')].map(a => ({t:(a.innerText||'').trim().slice(0,40), h:a.href})).slice(0,15);
  const imgs = [...document.querySelectorAll('img')].map(i=>i.src).filter(s=>s.includes('vkuserphoto')).slice(0,5);
  const tabs = [...document.querySelectorAll('a')].map(a=>(a.innerText||'').trim()).filter(t=>/Альбом|Фото/.test(t)).slice(0,8);
  return JSON.stringify({links, imgs: imgs.length, tabs, text: document.body.innerText.match(/Альбом[^\n]{0,40}/g)}, null, 1);
})()
