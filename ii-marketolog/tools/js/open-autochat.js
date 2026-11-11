(() => {
  const el = [...document.querySelectorAll('a,button')].find(e => /Автоматизация чатов/.test(e.innerText||''));
  if (!el) return 'нет кнопки';
  if (el.href) return 'href: ' + el.href;
  el.click(); return 'нажал';
})()
