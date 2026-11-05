(() => {
  const t = document.body.innerText;
  const followers = (t.match(/([\d\s]+)\s*подписчик\w*/) || [])[0] || 'не видно';
  const manage = t.includes('Управление');
  const admin = t.includes('Вы подписаны');
  const canPost = t.includes('Создать пост') || t.includes('Что у вас нового') || [...document.querySelectorAll('*')].some(e => (e.placeholder||'').includes('Что у вас нового'));
  return JSON.stringify({ followers, manage, admin, canPost, url: location.href }, null, 1);
})()
