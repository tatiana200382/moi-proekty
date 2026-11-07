(() => {
  const sel = document.querySelector('[data-marker="type_of_trade/select"]');
  if (!sel) return 'нет селекта';
  sel.click();
  const opt = document.querySelector('[data-marker="type_of_trade/option(20060)"]');
  if (!opt) return 'открыл, но опции нет';
  opt.click();
  return 'выбрано: ' + (opt.innerText||'').trim();
})()
