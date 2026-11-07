(() => {
  const el = [...document.querySelectorAll('a,button')].find(e => /Пополнение кошелька/.test(e.innerText||''));
  if (!el) return 'кнопка не найдена';
  const href = el.href || '';
  el.click();
  return 'нажал «Пополнение кошелька» ' + href;
})()
