(() => {
  const info = [];
  document.querySelectorAll('tr').forEach((tr, i) => {
    const t = tr.innerText.replace(/\n+/g, ' | ').slice(0, 90);
    if (t.includes('Silver')) info.push(`tr#${i}: ${t}`);
  });
  return JSON.stringify({ rows: info, count: document.querySelectorAll('tr').length }, null, 1);
})()
