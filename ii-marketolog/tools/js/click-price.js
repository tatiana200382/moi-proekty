(() => {
  const els = [...document.querySelectorAll('*')].filter(
    (el) => el.children.length === 0 && /Проверьте актуальность/.test(el.textContent)
  );
  if (!els.length) return 'не найдено';
  els[0].click();
  return 'клик по «Проверьте актуальность»';
})()
