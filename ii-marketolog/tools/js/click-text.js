(() => {
  const label = window.__label;
  const el = [...document.querySelectorAll('a,button,[role=tab]')].find(e => (e.innerText||'').trim() === label);
  if (!el) return 'нет: ' + label;
  el.click();
  return 'нажал: ' + label;
})()
