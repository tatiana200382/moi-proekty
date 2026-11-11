(() => {
  const out=[];
  const sel=document.querySelector('[data-marker="sostav_buketa/select"]');
  if (!sel) return 'нет селекта состава';
  sel.scrollIntoView({block:'center'});
  sel.click(); out.push('открыл список');
  return JSON.stringify(out);
})()
