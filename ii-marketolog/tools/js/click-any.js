(() => {
  const label = "Новая история";
  const el = [...document.querySelectorAll('*')].find(e => (e.textContent||'').trim() === label && e.children.length <= 1);
  if (!el) return 'не найдено';
  let p = el;
  for (let i=0;i<4 && p;i++){
    const tag = p.tagName;
    if (tag === 'BUTTON' || tag === 'A' || p.getAttribute('role') || p.getAttribute('tabindex')) { p.click(); return 'нажал ' + tag + ' ' + (p.getAttribute('role')||''); }
    p = p.parentElement;
  }
  el.click(); return 'нажал сам элемент';
})()
