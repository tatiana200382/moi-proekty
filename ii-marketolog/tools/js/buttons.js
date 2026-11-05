(() => {
  const out = [];
  document.querySelectorAll('button, [role=button], a').forEach((el) => {
    const t = (el.innerText || '').trim();
    if (t && t.length < 40 && el.offsetParent !== null) out.push(`${el.tagName}: ${t.replace(/\n+/g, ' ')}`);
  });
  return JSON.stringify([...new Set(out)].slice(0, 40), null, 1);
})()
