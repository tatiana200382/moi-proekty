(() => {
  const items = [...document.querySelectorAll('*')].filter(e => e.children.length === 0 && e.textContent.trim() === 'MAX');
  if (!items.length) return 'нет пункта MAX';
  items[0].click();
  return 'выбран MAX';
})()
