(() => {
  const out = { url: location.href, tabs: [] };
  const cands = [...document.querySelectorAll('[data-marker], a, button, [role="tab"]')];
  for (const el of cands) {
    const t = (el.innerText || "").trim().replace(/\s+/g, " ");
    if (!t || t.length > 60) continue;
    if (!/^(Активные|С ошибками|Неопубликованные|Архив|Удалённые|Черновики)/.test(t)) continue;
    out.tabs.push({
      tag: el.tagName,
      text: t,
      marker: el.getAttribute("data-marker"),
      href: el.getAttribute("href"),
      clickable: el.getAttribute("data-marker") || el.tagName,
    });
  }
  // категории в фильтре слева
  out.filterCats = [...document.querySelectorAll('[data-marker*="category"], [class*="filter"] label')]
    .map((e) => (e.innerText || "").trim().replace(/\s+/g, " "))
    .filter((t) => t && t.length < 80)
    .slice(0, 40);
  return out;
})()
