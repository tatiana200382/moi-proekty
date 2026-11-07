(() => {
  const el = document.querySelector('[data-marker="description-html-editor"]') || document.querySelector('[contenteditable="true"]');
  if (!el) return 'нет редактора';
  el.scrollIntoView({block:'center'});
  const r = el.getBoundingClientRect();
  return JSON.stringify({x:Math.round(r.left+r.width/2), y:Math.round(r.top+40), tag:el.tagName, editable:el.getAttribute('contenteditable')});
})()
