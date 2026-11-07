(() => {
  const out = [];
  const set = Object.getOwnPropertyDescriptor(HTMLInputElement.prototype, 'value').set;
  const btn = [...document.querySelectorAll('input')].find(i => (i.placeholder||'').includes('Придумайте текст кнопки'));
  if (btn) { set.call(btn,'Написать'); btn.dispatchEvent(new Event('input',{bubbles:true})); out.push('кнопка: Написать'); } else out.push('нет поля кнопки');
  const link = [...document.querySelectorAll('input')].find(i => (i.placeholder||'').includes('ссылку'));
  if (link) { set.call(link,'https://vk.com/s_sflowers'); link.dispatchEvent(new Event('input',{bubbles:true})); out.push('ссылка: vk.com/s_sflowers'); } else out.push('нет поля ссылки');
  return JSON.stringify(out);
})()
