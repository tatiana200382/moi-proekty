(() => {
  const cards=[...document.querySelectorAll('[data-marker="item"]')];
  const rows=cards.map(c=>{
    const t=(c.innerText||'').replace(/\r/g,'');
    const lines=t.split('\n').map(s=>s.trim()).filter(Boolean);
    const title=(c.querySelector('[itemprop="name"], h3')?.innerText||'').trim();
    const price=(c.querySelector('[itemprop="price"], [data-marker="item-price"]')?.innerText||'').trim();
    const photos=(t.match(/(\d+)\s*фото/)||[])[1]||'';
    const promo=/Продвинуто|Реклама/.test(t);
    const parts=/Оплата частями/.test(t);
    const rv=(t.match(/(\d,\d)\s*·\s*(\d+)\s*отзыв/)||[]);
    const seller=(lines.find(l=>/^[А-ЯЁ][^·]{2,40}$/.test(l) && !/₽|фото|Продвинуто/.test(l))||'').slice(0,40);
    return {title:title.slice(0,80), price, photos, promo, parts, rating:rv[1]||'', reviews:rv[2]||'', seller};
  }).filter(r=>r.title);
  return JSON.stringify(rows);
})()
