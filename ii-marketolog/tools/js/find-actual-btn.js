(() => {
  const out = [];
  document.querySelectorAll('button, [class*=button], [role=button]').forEach((el) => {
    const t = (el.innerText || '').trim();
    if (t === 'Данные актуальны') out.push({ tag: el.tagName, cls: (el.className || '').toString().slice(0, 60), disabled: el.disabled });
  });
  return JSON.stringify(out, null, 1);
})()
