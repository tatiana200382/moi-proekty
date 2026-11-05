(() => {
  const els = [...document.querySelectorAll('*')].filter(
    (el) => el.children.length === 0 && /Проверьте актуальность/.test(el.textContent)
  );
  return JSON.stringify(
    els.map((el) => ({
      tag: el.tagName,
      href: el.href || null,
      parent: (el.parentElement?.innerText || '').replace(/\n+/g, ' | ').slice(0, 160),
      grand: (el.parentElement?.parentElement?.innerText || '').replace(/\n+/g, ' | ').slice(0, 200),
    })),
    null,
    1
  );
})()
