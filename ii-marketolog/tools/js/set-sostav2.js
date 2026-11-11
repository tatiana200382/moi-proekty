(() => {
  const s=document.querySelectorAll('select')[1];
  const want=["Розы","Гвоздики","Хризантемы"];
  const vals=[...s.options].filter(o=>want.includes(o.text.trim())).map(o=>o.value);
  const setter=Object.getOwnPropertyDescriptor(HTMLSelectElement.prototype,'value').set;
  setter.call(s, vals);
  s.dispatchEvent(new Event('change',{bubbles:true}));
  return JSON.stringify({vals, disabled:s.disabled, selected:[...s.selectedOptions].map(o=>o.text)});
})()
