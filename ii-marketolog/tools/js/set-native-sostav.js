(() => {
  const s=document.querySelectorAll('select')[1];
  if(!s) return 'нет select';
  const want=["Розы","Гвоздики","Хризантемы"];
  [...s.options].forEach(o=>{ o.selected = want.includes(o.text.trim()); });
  s.dispatchEvent(new Event('input',{bubbles:true}));
  s.dispatchEvent(new Event('change',{bubbles:true}));
  const sel=[...s.selectedOptions].map(o=>o.text.trim());
  return JSON.stringify({выбрано:sel});
})()
