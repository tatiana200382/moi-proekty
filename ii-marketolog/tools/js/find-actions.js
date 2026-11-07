(() => {
  const res = [];
  document.querySelectorAll('*').forEach(e => {
    if (e.children.length === 0) {
      const t = (e.textContent || '').trim();
      if (/^(Удалить|В архив|Снять|Снять с публикации|Опубликовать|Завершить)$/i.test(t)) {
        const r = e.getBoundingClientRect();
        res.push({ t, tag: e.tagName, y: Math.round(r.top), x: Math.round(r.left), visible: r.width > 0 });
      }
    }
  });
  return JSON.stringify(res.slice(0, 12), null, 1);
})()
