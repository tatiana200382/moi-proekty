(() => {
  const bc = document.querySelector('[data-marker="breadcrumbs"]');
  const crumbs = bc
    ? [...bc.querySelectorAll('a, span')]
        .map((e) => ({ t: (e.innerText || '').trim().replace(/\s+/g, ' '), h: e.href || null }))
        .filter((x) => x.t && x.t !== '/')
    : [];
  const title =
    document.querySelector('[data-marker="item-view/title-info"]')?.innerText ||
    document.title;
  const price =
    document.querySelector('[data-marker="item-view/item-price"]')?.innerText || null;
  const params = [...document.querySelectorAll('[data-marker="item-view/item-params"] li')].map(
    (li) => li.innerText.replace(/\s+/g, ' ')
  );
  const desc =
    document.querySelector('[data-marker="item-view/item-description"]')?.innerText || '';
  return {
    url: location.href,
    title: (title || '').trim(),
    price: (price || '').trim(),
    crumbs,
    params,
    descFirst: desc.slice(0, 300),
  };
})()
