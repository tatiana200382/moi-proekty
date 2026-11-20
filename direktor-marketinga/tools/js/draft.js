(() => {
  const t = (s) => (s || "").trim().replace(/\s+/g, " ");
  const markers = [...document.querySelectorAll('[data-marker]')]
    .map((e) => e.getAttribute('data-marker'))
    .filter((m) => /categ|breadcrumb|title|field|step|draft/i.test(m));
  return {
    url: location.href,
    title: document.title,
    h1: t(document.querySelector('h1')?.innerText),
    allH: [...document.querySelectorAll('h1,h2,h3')].map((h) => t(h.innerText)).filter(Boolean).slice(0, 20),
    markers: [...new Set(markers)].slice(0, 60),
    text: document.body.innerText.slice(0, 3500),
  };
})()
