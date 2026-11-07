(() => {
  const b = document.querySelector('button[data-marker="category-title"]');
  if (!b) return 'нет';
  b.click();
  return 'нажал category-title: ' + (b.innerText||'').trim().slice(0,40);
})()
