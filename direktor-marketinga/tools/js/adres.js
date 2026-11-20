(() => {
  const t = (s) => (s || "").trim().replace(/\s+/g, " ");
  const m = document.querySelector('[data-marker="item-view/item-address"]');
  const map = document.querySelector('[data-marker="map"]');
  const geo = [...document.querySelectorAll('[data-marker*="geo"], [class*="style-item-address"], [itemprop="address"]')]
    .map((e) => t(e.innerText)).filter(Boolean).slice(0, 5);
  return {
    url: location.href,
    address: t(m?.innerText),
    geo,
    mapText: t(map?.innerText).slice(0, 200),
    desc: t(document.querySelector('[data-marker="item-view/item-description"]')?.innerText).slice(0, 600),
  };
})()
