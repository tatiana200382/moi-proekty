(() => {
  let closed = 0;
  document.querySelectorAll('[aria-label="Закрыть"], [data-marker="popup/close"], button').forEach(b => {
    const a = (b.getAttribute('aria-label') || b.innerText || '').trim();
    if (a === 'Закрыть' || a === '×' || /закры/i.test(b.className || '')) { try { b.click(); closed++; } catch(e){} }
  });
  return 'закрыто: ' + closed;
})()
