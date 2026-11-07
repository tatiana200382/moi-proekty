(() => {
  const inp = [...document.querySelectorAll('input')].find(i => i.value && i.value.includes('Букет на свидание'));
  if (!inp) return 'нет';
  const setter = Object.getOwnPropertyDescriptor(HTMLInputElement.prototype, 'value').set;
  setter.call(inp, '');
  inp.dispatchEvent(new Event('input', { bubbles: true }));
  return 'очищено';
})()
