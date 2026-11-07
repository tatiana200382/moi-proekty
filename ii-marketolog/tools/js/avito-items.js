(() => {
  const t = document.body.innerText.replace(/\n{2,}/g, '\n');
  const lines = t.split('\n').map(s => s.trim()).filter(Boolean);
  const idx = lines.findIndex(l => /^Активные/.test(l));
  const tail = lines.slice(idx, idx + 60);
  const titles = tail.filter(l => /₽|Букет|Цвет|Роз|Композиц|Набор|Доставка/i.test(l)).slice(0, 20);
  const counters = tail.filter(l => /Активные|С ошибками|Неопубликованные|Архив/.test(l)).slice(0, 4);
  return JSON.stringify({ counters, titles }, null, 1);
})()
