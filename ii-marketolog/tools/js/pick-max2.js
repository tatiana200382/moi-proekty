(() => {
  const items = [...document.querySelectorAll('*')].filter(e => e.children.length === 0 && e.textContent.trim() === 'MAX');
  if (!items.length) return 'MAX не найден в списке';
  items[items.length - 1].click();
  return 'выбран MAX';
})()
