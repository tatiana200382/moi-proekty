(() => {
  const boxes = [...document.querySelectorAll('input[type=checkbox]')];
  const top = boxes.find(c => { const r = c.getBoundingClientRect(); return r.top > 0 && r.top < 60; });
  if (!top) return 'не нашёл верхний чекбокс';
  top.click();
  return 'клик по верхнему чекбоксу, теперь: ' + top.checked;
})()
