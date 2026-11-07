(() => {
  const links = [...document.querySelectorAll('a')].filter(a => /Неопубликованные/.test(a.innerText || ''));
  if (!links.length) return 'нет ссылки';
  links[0].click();
  return 'открыл Неопубликованные: ' + links[0].href;
})()
