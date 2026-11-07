(() => {
  const inputs = [...document.querySelectorAll('input')];
  const t = inputs[3];
  const setter = Object.getOwnPropertyDescriptor(HTMLInputElement.prototype, 'value').set;
  setter.call(t, '+79312890203');
  t.dispatchEvent(new Event('input', { bubbles: true }));
  t.dispatchEvent(new Event('change', { bubbles: true }));
  t.dispatchEvent(new Event('blur', { bubbles: true }));
  return 'вписано: ' + t.value;
})()
