(() => {
  const t = document.body.innerText.replace(/\n{2,}/g, '\n');
  const lines = t.split('\n').map(s => s.trim()).filter(Boolean);
  const start = lines.findIndex(l => /₽/.test(l));
  return JSON.stringify(lines.slice(Math.max(0,start-25), start+70), null, 1);
})()
