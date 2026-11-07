(() => {
  const out = [];
  const p = document.querySelector('[data-marker="price"]');
  const pin = p ? (p.querySelector('input') || p) : null;
  if (pin && pin.tagName === 'INPUT') {
    const set = Object.getOwnPropertyDescriptor(HTMLInputElement.prototype, 'value').set;
    set.call(pin, '3850'); pin.dispatchEvent(new Event('input',{bubbles:true})); pin.dispatchEvent(new Event('change',{bubbles:true}));
    out.push('цена: ' + pin.value);
  } else out.push('цена: не найдено');
  const ce = document.querySelector('[contenteditable="true"]');
  out.push('описание: ' + (ce ? (ce.innerText||'').length + ' симв.' : 'нет редактора'));
  return JSON.stringify(out);
})()
