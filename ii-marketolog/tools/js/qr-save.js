(() => { const b=[...document.querySelectorAll('button')].find(x=>/^Сохранить/.test((x.innerText||'').trim())); if(!b) return 'нет кнопки'; b.click(); return 'сохранил'; })()
