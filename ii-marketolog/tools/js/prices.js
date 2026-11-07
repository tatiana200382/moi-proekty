(() => {
  const cards = [...document.querySelectorAll('[data-marker="item"]')].slice(0, 12);
  const rows = cards.map(c => {
    const t = (c.querySelector('[itemprop="name"], h3')?.innerText || '').trim().slice(0, 60);
    const p = (c.querySelector('[itemprop="price"], [data-marker="item-price"]')?.innerText || '').replace(/\s/g,' ').trim();
    return t + ' — ' + p;
  }).filter(r => /₽/.test(r));
  return JSON.stringify(rows, null, 1);
})()
