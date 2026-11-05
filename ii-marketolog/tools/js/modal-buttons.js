(() => {
  const dlg = document.querySelector('[role=dialog]') || document.querySelector('.Modal') || document.body;
  const btns = [...dlg.querySelectorAll('button')].map((b) => b.innerText.trim()).filter(Boolean);
  const inputs = [...dlg.querySelectorAll('input')].map((i) => ({ v: i.value, ph: i.placeholder }));
  return JSON.stringify({ buttons: [...new Set(btns)], inputs: inputs.slice(0, 6) }, null, 1);
})()
