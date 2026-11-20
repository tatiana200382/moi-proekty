(() => {
  const pick = (sel) => {
    const el = document.querySelector(sel);
    return el ? (el.innerText || "").trim().replace(/\n{2,}/g, "\n") : null;
  };
  const crumbs = [...document.querySelectorAll('[class*="breadcrumb"] a, [class*="Breadcrumb"] a, nav a')]
    .map((a) => (a.innerText || "").trim())
    .filter(Boolean);
  const checked = [...document.querySelectorAll('input:checked')].map((i) => i.value).slice(0, 20);
  return {
    url: location.href,
    title: document.title,
    h1: pick("h1"),
    crumbs: crumbs.slice(0, 12),
    text: document.body.innerText.slice(0, 4000),
    checked,
  };
})()
