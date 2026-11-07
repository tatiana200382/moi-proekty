(() => {
  const inputs = [...document.querySelectorAll('input')];
  const t = inputs[3];
  const setter = Object.getOwnPropertyDescriptor(HTMLInputElement.prototype, 'value').set;
  setter.call(t, '');
  t.dispatchEvent(new Event('input', { bubbles: true }));
  t.dispatchEvent(new Event('change', { bubbles: true }));
  return 'очищено';
})()
