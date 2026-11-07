(() => {
  const opt = document.querySelector('[data-marker="geo/undefined/custom-option(0)"]');
  if (!opt) return 'нет опции';
  const r = opt.getBoundingClientRect();
  ['mousedown','mouseup','click'].forEach(t => opt.dispatchEvent(new MouseEvent(t,{bubbles:true,clientX:r.left+10,clientY:r.top+5})));
  return 'выбрал: ' + opt.innerText.trim();
})()
