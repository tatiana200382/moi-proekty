(() => {
  const addr = "Ленинский проспект, 56";
  const el = [...document.querySelectorAll('*')].find(e => (e.textContent||'').includes(addr) && (e.textContent||'').length < 200 && e.children.length <= 3);
  if (!el) return 'нет строки ' + addr;
  let p = el;
  for (let i=0;i<5 && p;i++){
    if (p.tagName === 'A' && p.href) { return 'ссылка: ' + p.href; }
    p = p.parentElement;
  }
  el.click();
  return 'клик по строке';
})()
