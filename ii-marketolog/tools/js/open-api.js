(() => {
  const el = [...document.querySelectorAll('a,button')].find(e => /Интеграция по API/.test(e.innerText||''));
  if (!el) return 'нет';
  if (el.href) return 'href: ' + el.href;
  el.click(); return 'нажал';
})()
