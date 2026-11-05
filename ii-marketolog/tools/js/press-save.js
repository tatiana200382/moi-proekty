(() => {
  const b = [...document.querySelectorAll('button')].find((x) => x.innerText.trim() === 'Сохранить изменения');
  if (!b) return 'кнопка не найдена';
  b.scrollIntoView({ block: 'center' });
  b.click();
  return 'нажато «Сохранить изменения»';
})()
