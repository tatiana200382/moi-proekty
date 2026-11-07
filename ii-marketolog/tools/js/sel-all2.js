(() => {
  const el = [...document.querySelectorAll('*')].find(e => e.children.length === 0 && /^Выбрать 7 из 7/.test(e.textContent.trim()));
  if (!el) return 'нет элемента';
  el.click();
  return 'клик по «Выбрать 7 из 7»';
})()
