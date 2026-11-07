(() => {
  const name = "Для дома и дачи";
  const btn = [...document.querySelectorAll('button[data-marker="category-wizard/button"]')].find(b => (b.innerText||'').trim() === name);
  if (!btn) return 'нет кнопки: ' + name + ' | есть: ' + [...document.querySelectorAll('button[data-marker="category-wizard/button"]')].map(b=>b.innerText.trim()).join(', ');
  btn.click();
  return 'нажал: ' + name;
})()
