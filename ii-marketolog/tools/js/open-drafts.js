(() => {
  const el = [...document.querySelectorAll('*')].find(e => e.children.length===0 && /^Черновики/.test((e.textContent||'').trim()));
  if (!el) return 'нет';
  el.click();
  return 'открыл Черновики';
})()
