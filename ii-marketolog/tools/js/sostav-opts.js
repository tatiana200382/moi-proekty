(() => {
  const opts=[...document.querySelectorAll('[data-marker^="sostav_buketa/option"]')].map(o=>({m:o.getAttribute('data-marker'), t:(o.innerText||'').trim()}));
  return JSON.stringify(opts.filter(o=>/Роз|Гвозд|Хризант/i.test(o.t)).slice(0,8));
})()
