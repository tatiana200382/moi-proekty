(() => {
  const out = [];
  const inp = [...document.querySelectorAll('input')].find(i => (i.placeholder||'').includes('Придумайте название'));
  if (inp) {
    const set = Object.getOwnPropertyDescriptor(HTMLInputElement.prototype, 'value').set;
    set.call(inp, 'Букет под повод');
    inp.dispatchEvent(new Event('input', {bubbles:true}));
    inp.dispatchEvent(new Event('change', {bubbles:true}));
    out.push('название: ' + inp.value);
  } else out.push('нет поля названия');
  const btns = [...document.querySelectorAll('button')].map(b => (b.innerText||'').trim()).filter(Boolean).slice(0,12);
  out.push('кнопки: ' + btns.join(' | '));
  return JSON.stringify(out);
})()
