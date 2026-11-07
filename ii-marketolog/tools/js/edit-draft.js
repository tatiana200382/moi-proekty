(() => {
  const b = [...document.querySelectorAll('button')].find(x => /^Редактиров/.test((x.innerText||'').trim()));
  if (!b) return 'нет кнопки';
  b.click();
  return 'открыл редактор черновика';
})()
