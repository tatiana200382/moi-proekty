(() => {
  const b = [...document.querySelectorAll('button')].find(x => /^Разместить/.test((x.innerText||'').trim()));
  if (!b) return 'нет кнопки Разместить';
  b.click();
  return 'нажал Разместить';
})()
