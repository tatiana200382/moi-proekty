(() => {
  const inputs = [...document.querySelectorAll('input')];
  const hasModal = document.body.innerText.includes('Редактировать товар');
  const vals = inputs.map((i) => i.value).filter((v) => v && v.length > 3).slice(0, 8);
  return JSON.stringify({
    modal: hasModal,
    inputCount: inputs.length,
    values: vals,
    buttons: [...new Set([...document.querySelectorAll('button')].map((b) => b.innerText.trim()).filter((t) => t && t.length < 30))].slice(0, 15),
  }, null, 1);
})()
