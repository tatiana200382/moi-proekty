(() => {
  const t = document.body.innerText;
  const i = t.indexOf('Ленинский');
  const links = [...document.querySelectorAll('[href*="/sprav/"]')].map(a=>a.href).slice(0,10);
  return JSON.stringify({found: i>=0, ctx: i>=0 ? t.slice(Math.max(0,i-120), i+160).replace(/\n{2,}/g,' ') : '', links});
})()
