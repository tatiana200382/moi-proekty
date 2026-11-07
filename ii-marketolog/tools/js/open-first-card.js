(() => {
  const links = [...document.querySelectorAll('a')].filter(a => /\/item\//.test(a.href));
  if (!links.length) return 'нет ссылок на объявления';
  links[0].click();
  return 'открыл: ' + links[0].href.slice(0, 80);
})()
