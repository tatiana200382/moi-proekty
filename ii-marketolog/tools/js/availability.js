(() => {
  const labels = [...document.querySelectorAll('label')].filter(l => /В наличии/.test(l.innerText||''));
  if (labels.length) { const inp = labels[0].querySelector('input'); if (inp) { inp.click(); return 'нажал В наличии (label)'; } labels[0].click(); return 'клик по label'; }
  const radios = [...document.querySelectorAll('input[type=radio]')];
  if (radios.length) { radios[0].click(); return 'радио #0'; }
  return 'не нашёл';
})()
