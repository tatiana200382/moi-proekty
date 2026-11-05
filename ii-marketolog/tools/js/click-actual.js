(() => {
  const els = [...document.querySelectorAll('button, [role=button], div, span, a')].filter(
    (el) => el.children.length <= 1 && el.textContent.trim() === 'Данные актуальны'
  );
  if (!els.length) return 'кнопка не найдена';
  els[0].click();
  return 'нажато «Данные актуальны»';
})()
