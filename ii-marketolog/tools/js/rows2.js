(() => {
  const txt = document.body.innerText.replace(/\n{2,}/g, '\n');
  const lines = txt.split('\n');
  const out = [];
  for (let i = 0; i < lines.length; i++) {
    const l = lines[i].trim();
    if (/₽/.test(l)) out.push(`${lines[i - 1]?.trim()} → ${l}`);
  }
  return JSON.stringify(out.slice(0, 25), null, 1);
})()
