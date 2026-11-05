(() => {
  const input = [...document.querySelectorAll('input')].find((i) => i.value.includes('будут лизиантусов'));
  if (!input) return 'поле не найдено';
  const setter = Object.getOwnPropertyDescriptor(HTMLInputElement.prototype, 'value').set;
  setter.call(input, 'Букет лизиантусов (9 шт)');
  input.dispatchEvent(new Event('input', { bubbles: true }));
  input.dispatchEvent(new Event('change', { bubbles: true }));
  const btn = [...document.querySelectorAll('button')].find((b) => b.innerText.trim() === 'Внести изменения');
  if (!btn) return 'кнопка сохранения не найдена';
  btn.click();
  return 'название изменено и отправлено';
})()
