(() => {
  const el = [...document.querySelectorAll('a,button,div,span')].find(e => e.children.length<=1 && /Другая категория/.test(e.textContent||''));
  if (!el) return 'нет кнопки';
  el.click();
  return 'нажал Другая категория';
})()
