(() => {
  const el = [...document.querySelectorAll('*')].find(e => (e.textContent||'').trim().endsWith('Новая история') && (e.textContent||'').length < 40);
  if (!el) return 'нет';
  let p = el;
  for (let i=0;i<4 && p;i++){ if (p.getAttribute && p.getAttribute('tabindex') !== null) break; p = p.parentElement; }
  const target = p || el;
  target.setAttribute('tabindex','0');
  target.focus();
  const r = target.getBoundingClientRect();
  ['pointerdown','mousedown','pointerup','mouseup','click'].forEach(t => target.dispatchEvent(new MouseEvent(t,{bubbles:true, clientX:r.left+5, clientY:r.top+5})));
  return 'фокус и клик по ' + target.tagName + ' ' + Math.round(r.left) + ',' + Math.round(r.top);
})()
