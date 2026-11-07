(() => {
  const opts = [...document.querySelectorAll('[data-marker^="type_of_trade/option"]')].map(o => ({ m: o.getAttribute('data-marker'), t: (o.innerText||'').trim() }));
  return JSON.stringify(opts, null, 1);
})()
