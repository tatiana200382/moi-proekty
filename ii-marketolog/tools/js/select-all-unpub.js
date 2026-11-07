(() => {
  const cb = [...document.querySelectorAll('input[type=checkbox]')].find(c => (c.closest('label')||c.parentElement)?.innerText?.includes('Выбрать'));
  if (!cb) return 'нет чекбокса «Выбрать»';
  cb.click();
  return 'выбраны все: ' + ((cb.closest('label')||cb.parentElement)?.innerText||'').slice(0,40);
})()
