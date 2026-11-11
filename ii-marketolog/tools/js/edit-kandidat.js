(() => {
  const blocks = [...document.querySelectorAll('*')].filter(e => (e.textContent||'').includes('Кандидатам на вакансию') && (e.textContent||'').length < 300);
  if (!blocks.length) return 'нет блока';
  const block = blocks[blocks.length-1];
  let p = block;
  for (let i=0;i<6 && p;i++){
    const btn = p.querySelector && [...p.querySelectorAll('button')].find(b=>{const r=b.getBoundingClientRect(); return r.width>0 && r.width<60 && (b.innerText||'').trim()==='';});
    if (btn) { btn.click(); return 'нажал кнопку редактирования'; }
    p = p.parentElement;
  }
  return 'кнопка не найдена';
})()
