(() => {
  const buttons = [...document.querySelectorAll('*')].filter(
    (el) => el.children.length === 0 && el.textContent.trim() === 'Обновить данные'
  );
  const out = buttons.map((b) => {
    const chain = [];
    let p = b;
    for (let i = 0; i < 12 && p; i++) {
      p = p.parentElement;
      if (!p) break;
      const t = (p.innerText || '').replace(/\n+/g, ' | ');
      chain.push(`${p.tagName}.${(p.className || '').toString().slice(0, 25)} :: ${t.slice(0, 70)}`);
    }
    return { text: b.innerText, chain: chain.slice(0, 5) };
  });
  return JSON.stringify(out, null, 1);
})()
