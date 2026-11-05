(() => {
  const el = [...document.querySelectorAll('*')].find((x) => x.children.length === 0 && x.textContent.trim() === 'Бекет цветов в сумочке');
  if (!el) return 'не найдено';
  el.scrollIntoView({ block: 'center' });
  el.click();
  return 'открыт';
})()
