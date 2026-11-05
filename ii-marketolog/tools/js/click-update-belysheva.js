(() => {
  const buttons = [...document.querySelectorAll('*')].filter(
    (el) => el.children.length === 0 && el.textContent.trim() === 'Обновить данные'
  );
  for (const el of buttons) {
    let p = el;
    for (let i = 0; i < 8 && p; i++) {
      p = p.parentElement;
      if (p && p.innerText && p.innerText.includes('Белышева')) {
        el.click();
        return 'clicked БЕЛЫШЕВА';
      }
    }
  }
  return 'кнопка не найдена';
})()
