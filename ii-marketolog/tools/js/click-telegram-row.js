(() => {
  const els = [...document.querySelectorAll('*')].filter(e => e.children.length === 0 && e.textContent.trim() === 'Telegram');
  if (!els.length) return 'нет Telegram';
  let el = els[0];
  el.click();
  return 'клик по строке Telegram';
})()
