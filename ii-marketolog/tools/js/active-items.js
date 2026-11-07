(() => {
  const cards = [...document.querySelectorAll('div')].filter(d => {
    const t = d.innerText || '';
    return /₽/.test(t) && (t.length < 400) && /дней на Авито|сегодня|Активно|Просмотры/.test(t);
  });
  return JSON.stringify([...new Set(cards.map(c => (c.innerText||'').replace(/\n+/g,' | ').slice(0,150)))].slice(0,8), null, 1);
})()
