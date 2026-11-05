(() => {
  const target = "Букет цветов " Ароматы любви"";
  const el = [...document.querySelectorAll('*')].find((x) => x.children.length === 0 && x.textContent.trim() === target);
  if (!el) return 'НЕ НАЙДЕНО: ' + target;
  el.scrollIntoView({ block: 'center' });
  el.click();
  return 'открыт: ' + target;
})()
