(() => {
  const btns = [...document.querySelectorAll('button')].filter(b => (b.getAttribute('aria-label')||'') === 'очистить');
  btns.forEach(b => { try { b.click(); } catch(e){} });
  return 'нажал кнопок очистить: ' + btns.length;
})()
