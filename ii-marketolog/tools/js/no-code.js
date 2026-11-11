(() => { const el=[...document.querySelectorAll('a,button,span')].find(e=>/Моего кода нет в списке/.test(e.innerText||'')); if(!el) return 'нет ссылки'; el.click(); return 'нажал'; })()
