(() => {
  const inputs = [...document.querySelectorAll('input')];
  const target = inputs[3];
  const setter = Object.getOwnPropertyDescriptor(HTMLInputElement.prototype, 'value').set;
  setter.call(target, '+79312890203');
  target.dispatchEvent(new Event('input', { bubbles: true }));
  target.dispatchEvent(new Event('change', { bubbles: true }));
  return 'вписано: ' + target.value;
})()
