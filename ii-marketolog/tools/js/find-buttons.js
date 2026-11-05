(() => {
  const res = [];
  document.querySelectorAll('*').forEach((el) => {
    if (el.children.length === 0 && el.textContent.trim() === 'Обновить данные') {
      let p = el, ctx = '';
      for (let i = 0; i < 8 && p; i++) {
        p = p.parentElement;
        if (p && p.innerText && p.innerText.length > 30) { ctx = p.innerText.replace(/\n+/g, ' | ').slice(0, 140); break; }
      }
      res.push(ctx);
    }
  });
  return JSON.stringify(res, null, 1);
})()
