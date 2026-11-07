(() => {
  const els = [...document.querySelectorAll('*')].filter(e => e.children.length === 0 && /^Неопубликованные/.test(e.textContent.trim()));
  if (!els.length) return 'не найдено';
  els[0].click();
  return 'клик по Неопубликованные';
})()
