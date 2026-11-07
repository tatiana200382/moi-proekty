(() => {
  const a = [...document.querySelectorAll('a')].find(e => e.textContent.trim()==='Обновить данные');
  if (!a) return 'нет';
  a.click();
  return 'клик: ' + (a.href || 'без href');
})()
