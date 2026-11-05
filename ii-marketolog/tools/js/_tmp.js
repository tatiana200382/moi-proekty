
(() => {
  const oldName = "Бекет цветов в сумочке";
  const newName = "Букет с розами в сумочке";
  const input = [...document.querySelectorAll('input')].find(i => i.value.trim() === oldName);
  if (!input) return 'ПОЛЕ НЕ НАЙДЕНО';
  const setter = Object.getOwnPropertyDescriptor(HTMLInputElement.prototype, 'value').set;
  setter.call(input, newName);
  input.dispatchEvent(new Event('input', { bubbles: true }));
  input.dispatchEvent(new Event('change', { bubbles: true }));
  const btn = [...document.querySelectorAll('button')].find(b => b.innerText.trim() === 'Внести изменения');
  if (!btn) return 'КНОПКА НЕ НАЙДЕНА';
  btn.click();
  return 'СОХРАНЕНО';
})()
