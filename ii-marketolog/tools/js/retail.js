(() => {
  const cards = [...document.querySelectorAll('[data-marker="item"]')];
  const rows = [];
  cards.forEach(c => {
    const t = c.innerText;
    const title = (c.querySelector('[itemprop="name"], h3')?.innerText || '').trim();
    const priceTxt = (c.querySelector('[itemprop="price"], [data-marker="item-price"]')?.innerText || '').trim();
    const num = parseInt(priceTxt.replace(/[^\d]/g, ''), 10) || 0;
    const rating = (t.match(/(\d,\d)\s*·\s*(\d+)\s*отзыв/) || []);
    if (num >= 1500 && title) rows.push({ title: title.slice(0, 70), price: priceTxt, rating: rating[1] ? `${rating[1]}·${rating[2]}` : '', desc: (t.split('\n').find(l => l.length > 60) || '').slice(0, 80) });
  });
  return JSON.stringify(rows.slice(0, 15), null, 1);
})()
