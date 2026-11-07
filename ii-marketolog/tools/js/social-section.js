(() => {
  const t = document.body.innerText;
  const i = t.indexOf('Сайт и социальные сети');
  const block = t.slice(i, i + 400).replace(/\n{2,}/g, '\n');
  const inputs = [...document.querySelectorAll('input,select')].map(e => e.value || e.placeholder || '').filter(v => v && v.length < 60);
  return JSON.stringify({ block, inputs: [...new Set(inputs)].slice(0, 15) }, null, 1);
})()
