(() => {
  const buttons = [...document.querySelectorAll('*')].filter(
    (el) => el.children.length === 0 && el.textContent.trim() === 'Обновить данные'
  );
  if (buttons.length < 2) return 'кнопок меньше двух: ' + buttons.length;
  buttons[1].click();
  return 'нажата вторая кнопка (5,0 / 117 — Белышева)';
})()
