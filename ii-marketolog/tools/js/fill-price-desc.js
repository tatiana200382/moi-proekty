(() => {
  const out = [];
  const price = document.querySelector('[data-marker="price"] input, input[data-marker="price"]');
  const priceEl = price || document.querySelector('input[name="price"], [data-marker="price"]');
  if (priceEl && priceEl.tagName === 'INPUT') {
    const set = Object.getOwnPropertyDescriptor(HTMLInputElement.prototype, 'value').set;
    set.call(priceEl, '1950');
    priceEl.dispatchEvent(new Event('input', {bubbles:true}));
    priceEl.dispatchEvent(new Event('change', {bubbles:true}));
    priceEl.dispatchEvent(new Event('blur', {bubbles:true}));
    out.push('цена: 1950');
  } else out.push('цена: поле не найдено (' + (priceEl?.tagName||'нет') + ')');

  const desc = document.querySelector('[data-marker="description"] textarea, textarea[data-marker="description"], [data-marker="field/description"] textarea');
  if (desc) {
    const set = Object.getOwnPropertyDescriptor(HTMLTextAreaElement.prototype, 'value').set;
    set.call(desc, `Букет под ваш повод, а не «как на картинке».`);
    desc.dispatchEvent(new Event('input', {bubbles:true}));
    out.push('описание: заполнено');
  } else out.push('описание: поле не найдено');
  return JSON.stringify(out);
})()
