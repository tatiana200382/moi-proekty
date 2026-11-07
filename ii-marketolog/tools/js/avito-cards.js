(() => {
  const cards = [...document.querySelectorAll('div')].filter(d => {
    const t = d.innerText || '';
    return /₽|Зарплата не указана/.test(t) && /дней на Авито|Истёк срок|Ждут активации/.test(t) && t.length < 400;
  });
  const out = cards.map(c => (c.innerText || '').replace(/\n+/g, ' | ').slice(0, 160));
  return JSON.stringify([...new Set(out)].slice(0, 12), null, 1);
})()
