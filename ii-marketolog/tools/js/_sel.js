(() => {
  const idx = Number(window.__sel);
  const value = "Товар приобретён на продажу";
  const s = document.querySelectorAll('select')[idx];
  if (!s) return 'нет селекта ' + idx;
  const opt = [...s.options].find(o => o.text.trim() === value);
  if (!opt) return 'нет опции: ' + value + ' | есть: ' + [...s.options].map(o=>o.text.trim()).slice(0,6).join(', ');
  const setter = Object.getOwnPropertyDescriptor(HTMLSelectElement.prototype, 'value').set;
  setter.call(s, opt.value);
  s.dispatchEvent(new Event('change', { bubbles: true }));
  return 'выбрано: ' + value;
})()
