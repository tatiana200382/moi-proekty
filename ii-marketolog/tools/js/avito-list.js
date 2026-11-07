(() => {
  const links = [...document.querySelectorAll('a[href*="/item/"]')];
  const seen = new Set(); const out = [];
  links.forEach(a => {
    const href = a.href.split('?')[0];
    if (seen.has(href)) return;
    const txt = (a.innerText || '').replace(/\n+/g, ' | ').trim();
    if (!txt) return;
    seen.add(href);
    out.push({ txt: txt.slice(0, 120), href });
  });
  return JSON.stringify(out.slice(0, 20), null, 1);
})()
