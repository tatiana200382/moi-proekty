(() => {
  const lab = [...document.querySelectorAll('*')].find(e => e.children.length===0 && (e.textContent||'').trim()==='Вид объявления');
  if (!lab) return 'нет метки';
  let box = lab.parentElement;
  const html = box.outerHTML;
  return JSON.stringify({ snippet: html.slice(0, 900) }, null, 1);
})()
