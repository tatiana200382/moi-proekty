(() => {
  const b = [...document.querySelectorAll('button')].find(x => /^Продолжить/.test((x.innerText||'').trim()));
  if (!b) return 'нет';
  b.click(); return 'нажал Продолжить';
})()
