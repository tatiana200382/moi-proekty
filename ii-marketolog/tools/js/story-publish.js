(() => {
  const b = [...document.querySelectorAll('button')].find(x => /^Опубликовать/.test((x.innerText||'').trim()));
  if (!b) return 'нет кнопки';
  b.click();
  return 'нажал Опубликовать';
})()
