(() => {
  const btns = [...document.querySelectorAll('button')].map(b => b.getAttribute('aria-label')||b.innerText.trim()).filter(Boolean);
  return JSON.stringify([...new Set(btns)].slice(0,15));
})()
