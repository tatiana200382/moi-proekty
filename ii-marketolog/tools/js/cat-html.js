(() => {
  const el = [...document.querySelectorAll('*')].find(e => e.children.length <= 1 && (e.textContent||'').trim() === 'Другая категория');
  if (!el) return 'нет';
  return JSON.stringify({ self: el.outerHTML.slice(0,200), parent: el.parentElement.outerHTML.slice(0,400) }, null, 1);
})()
