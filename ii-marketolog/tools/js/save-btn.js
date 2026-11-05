(() => {
  const btns = [...document.querySelectorAll('button')].map((b) => b.innerText.trim()).filter((t) => t && t.length < 40);
  return JSON.stringify([...new Set(btns)], null, 1);
})()
