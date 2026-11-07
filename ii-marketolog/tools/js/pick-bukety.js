(() => {
  const el = [...document.querySelectorAll('*')].find(e => e.children.length <= 2 && /^Букеты · Растения/.test((e.textContent||'').trim()));
  if (!el) return 'нет варианта Букеты';
  el.click();
  return 'выбрал: ' + (el.textContent||'').trim().slice(0,40);
})()
