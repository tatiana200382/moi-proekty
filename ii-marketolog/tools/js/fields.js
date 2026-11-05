(() => {
  const out = [];
  document.querySelectorAll('input').forEach((i) => {
    if (i.value && i.value.length < 80) out.push(`${i.name || i.id || i.type}: ${i.value}`);
  });
  return JSON.stringify(out.slice(0, 25), null, 1);
})()
