(() => {
  const oldName = "__OLD__";
  const newName = "__NEW__";
  const input = [...document.querySelectorAll('input')].find((i) => i.value.trim() === oldName);
  if (!input) return 'поле не найдено';
  const setter = Object.getOwnPropertyDescriptor(HTMLInputElement.prototype, 'value').set;
  setter.call(input, newName);
  input.dispatchEvent(new Event('input', { bubbles: true }));
  input.dispatchEvent(new Event('change', { bubbles: true }));
  const btn = [...document.querySelectorAll('button')].find((b) => b.innerText.trim() === 'Внести изменения');
  if (!btn) return 'кнопка не найдена';
  btn.click();
  return 'сохранено: ' + newName;
})()
