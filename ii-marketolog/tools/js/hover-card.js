(() => {
  const cards = [...document.querySelectorAll('div')].filter(d => /₽|Зарплата не указана/.test(d.innerText||'') && /дней на Авито|Истёк срок/.test(d.innerText||'') && (d.innerText||'').length < 400);
  if (!cards.length) return 'нет карточек';
  const c = cards[0];
  const r = c.getBoundingClientRect();
  ['pointerover','mouseover','mouseenter','pointerenter','mousemove'].forEach(type => {
    c.dispatchEvent(new MouseEvent(type, {bubbles:true, clientX:r.left+10, clientY:r.top+10}));
  });
  return 'навели на карточку: ' + (c.innerText||'').replace(/\n+/g,' ').slice(0,50);
})()
