(() => {
  const btn = [...document.querySelectorAll('button')].find((b) => b.innerText.trim() === 'Данные актуальны');
  if (!btn) return 'не найдено';
  btn.scrollIntoView({ block: 'center' });
  btn.click();
  return 'нажата кнопка «Данные актуальны»';
})()
