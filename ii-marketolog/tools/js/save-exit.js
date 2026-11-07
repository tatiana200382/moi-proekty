(() => {
  const b = [...document.querySelectorAll('button')].find(x => /Сохранить и выйти/.test(x.innerText||''));
  if (!b) return 'кнопки нет';
  b.click();
  return 'нажал Сохранить и выйти';
})()
