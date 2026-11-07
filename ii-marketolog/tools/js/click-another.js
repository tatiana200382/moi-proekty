(() => {
  const btn = document.querySelector('button[data-marker="another-category"]');
  if (!btn) return 'кнопки нет';
  btn.click();
  return 'нажал another-category';
})()
