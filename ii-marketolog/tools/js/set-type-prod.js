(() => {
  const s=document.querySelectorAll('select')[0];
  if(!s) return 'нет select';
  const opt=[...s.options].find(o=>/производител/i.test(o.text));
  if(!opt) return 'нет опции';
  const set=Object.getOwnPropertyDescriptor(HTMLSelectElement.prototype,'value').set;
  set.call(s,opt.value); s.dispatchEvent(new Event('change',{bubbles:true}));
  return 'вид: '+opt.text;
})()
