(() => {
  const inputs = [...document.querySelectorAll('input')];
  const target = inputs[3];
  if (!target) return 'поле MAX не найдено';
  const setter = Object.getOwnPropertyDescriptor(HTMLInputElement.prototype, 'value').set;
  setter.call(target, 'https://max.ru/u/79312890203');
  target.dispatchEvent(new Event('input', { bubbles: true }));
  target.dispatchEvent(new Event('change', { bubbles: true }));
  return 'вписано: ' + target.value;
})()
