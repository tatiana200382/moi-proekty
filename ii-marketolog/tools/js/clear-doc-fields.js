(() => {
  const bad = ["Данные не нужны","Данные ненужные","данные не нужны"];
  const set = Object.getOwnPropertyDescriptor(HTMLInputElement.prototype,'value').set;
  let n=0;
  [...document.querySelectorAll('input')].forEach(i=>{
    if (i.getBoundingClientRect().top>0 && bad.includes((i.value||'').trim())) {
      set.call(i,''); i.dispatchEvent(new Event('input',{bubbles:true})); i.dispatchEvent(new Event('change',{bubbles:true})); n++;
    }
  });
  return 'очищено полей: '+n;
})()
