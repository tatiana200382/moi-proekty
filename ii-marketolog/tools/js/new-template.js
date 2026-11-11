(() => {
  const el = [...document.querySelectorAll('button,a,[role=button]')].find(e => /Новый шаблон/.test(e.innerText||''));
  if (!el) return 'нет кнопки';
  el.click(); return 'нажал Новый шаблон';
})()
