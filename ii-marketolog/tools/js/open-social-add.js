(() => {
  const heads = [...document.querySelectorAll('*')].filter(e => e.children.length === 0 && e.textContent.trim() === 'Сайт и социальные сети');
  if (!heads.length) return 'нет заголовка';
  let box = heads[0];
  for (let i = 0; i < 6 && box; i++) {
    const btn = [...box.querySelectorAll('button')].find(b => b.innerText.trim() === 'Добавить');
    if (btn) { btn.click(); return 'нажал Добавить в блоке «Сайт и социальные сети»'; }
    box = box.parentElement;
  }
  return 'кнопка Добавить не найдена в блоке';
})()
