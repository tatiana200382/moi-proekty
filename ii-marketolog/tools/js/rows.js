(() => {
  const rows = [...document.querySelectorAll('tr, [class*=Row]')]
    .map((r) => (r.innerText || '').replace(/\n+/g, ' | ').trim())
    .filter((t) => t.length > 10 && t.length < 90 && /₽/.test(t));
  return JSON.stringify([...new Set(rows)].slice(0, 22), null, 1);
})()
