(() => {
  const cards = [...document.querySelectorAll('[data-marker="item"]')];
  const out = cards.slice(0, 30).map(c => {
    const title = c.querySelector('[itemprop="name"], h3')?.innerText?.trim() || '';
    const price = c.querySelector('[itemprop="price"], [data-marker="item-price"]')?.innerText?.trim() || '';
    const seller = (c.innerText.match(/\n([^\n]{3,60})\n\d,\d/) || [])[1] || '';
    const rating = (c.innerText.match(/(\d,\d)\s*·\s*(\d+)\s*отзыв/) || []);
    const desc = (c.innerText.split('\n').find(l => l.length > 60) || '').slice(0, 90);
    return { title, price, seller, rating: rating[1] ? `${rating[1]} · ${rating[2]} отз.` : '', desc };
  });
  return JSON.stringify(out, null, 1);
})()
