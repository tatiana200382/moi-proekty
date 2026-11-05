(() => {
  const el = [...document.querySelectorAll('*')].find(
    (x) => x.children.length === 0 && x.textContent.trim() === 'будут лизиантусов (9 шт)'
  );
  if (!el) return 'не найдено';
  el.scrollIntoView({ block: 'center' });
  el.click();
  return 'клик по названию товара';
})()
