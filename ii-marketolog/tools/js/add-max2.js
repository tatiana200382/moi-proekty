(() => {
  const heads = [...document.querySelectorAll('*')].filter(e => e.children.length === 0 && e.textContent.trim() === 'Сайт и социальные сети');
  let box = heads[0];
  for (let i = 0; i < 6 && box; i++) {
    const btn = [...box.querySelectorAll('button')].find(b => b.innerText.trim() === 'Добавить');
    if (btn) { btn.click(); break; }
    box = box.parentElement;
  }
  return 'открыл список соцсетей';
})()
