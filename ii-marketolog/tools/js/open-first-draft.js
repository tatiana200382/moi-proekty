(() => {
  const els = [...document.querySelectorAll('a,button')].filter(e => /Редактиров/.test(e.innerText||''));
  if (!els.length) return 'нет кнопки';
  const el = els[els.length-1];
  if (el.href) return 'href: ' + el.href;
  el.click(); return 'нажал Редактировать';
})()
