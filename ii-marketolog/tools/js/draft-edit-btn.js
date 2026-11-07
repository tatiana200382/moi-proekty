(() => {
  const els = [...document.querySelectorAll('a,button')].map(e => ({t:(e.innerText||'').trim(), h:e.href||''})).filter(x => /Редактиров|Продолжить|Завершить/i.test(x.t));
  return JSON.stringify(els.slice(0,6), null, 1);
})()
