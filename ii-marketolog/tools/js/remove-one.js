(() => {
  const btns=[...document.querySelectorAll('button')].filter(b=>{const r=b.getBoundingClientRect(); return r.width>10&&r.width<40&&r.top>500&&r.top<900;});
  const x=btns.find(b=>{const r=b.getBoundingClientRect(); return Math.round(r.left+r.width/2)>150 && Math.round(r.left+r.width/2)<300;});
  if(!x) return 'нет кнопки';
  x.click(); return 'удалил фото';
})()
