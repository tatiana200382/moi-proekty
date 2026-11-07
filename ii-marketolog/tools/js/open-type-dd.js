(() => {
  const lab = [...document.querySelectorAll('*')].find(e => e.children.length===0 && (e.textContent||'').trim()==='Вид объявления');
  if (!lab) return 'нет метки';
  let box = lab.parentElement;
  for (let i=0;i<4&&box;i++){
    const clickable = box.querySelector('[role=combobox], [data-marker*=select], button, div[tabindex]');
    if (clickable) { clickable.click(); return 'нажал: ' + (clickable.tagName + ' ' + (clickable.getAttribute('data-marker')||'')); }
    box = box.parentElement;
  }
  return 'не нашёл кликабельного';
})()
