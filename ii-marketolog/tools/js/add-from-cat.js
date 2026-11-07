(() => {
  const a = [...document.querySelectorAll('a')].find(x => /Разместить объявление/.test(x.innerText||''));
  if (!a) return 'нет ссылки';
  const href = a.href;
  a.click();
  return 'клик: ' + href;
})()
