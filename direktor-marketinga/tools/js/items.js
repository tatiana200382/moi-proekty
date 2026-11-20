(() => {
  const cards = [...document.querySelectorAll('[data-marker^="item-snippet/"]')];
  const items = cards.map((c) => {
    const a = c.querySelector("a[href]");
    const txt = (c.innerText || "")
      .split("\n")
      .map((s) => s.trim())
      .filter(Boolean);
    return {
      marker: c.getAttribute("data-marker"),
      href: a ? a.href : null,
      title: txt[0] || null,
      lines: txt.slice(0, 14),
    };
  });
  return {
    url: location.href,
    tabs: [...document.querySelectorAll('[data-marker^="profile-items-tab/tab"]')].map((b) => ({
      marker: b.getAttribute("data-marker"),
      text: (b.innerText || "").trim().replace(/\s+/g, " "),
      selected: b.getAttribute("aria-selected") || b.getAttribute("aria-pressed") || null,
    })),
    count: items.length,
    items,
    headText: document.body.innerText.slice(0, 1800),
  };
})()
