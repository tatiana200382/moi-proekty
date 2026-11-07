(() => {
  const opt = document.querySelector('[data-marker="type_of_trade/option(20060)"]');
  if (!opt) return 'опции нет';
  const r = opt.getBoundingClientRect();
  ['mousedown','mouseup','click'].forEach(t => opt.dispatchEvent(new MouseEvent(t, {bubbles:true, clientX:r.left+10, clientY:r.top+10})));
  return 'клик по опции, y=' + Math.round(r.top);
})()
