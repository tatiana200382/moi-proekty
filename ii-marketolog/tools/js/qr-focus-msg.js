(() => { const t=[...document.querySelectorAll('textarea')].find(x=>(x.placeholder||'').includes('Ваш текст')); if(!t) return 'нет'; t.focus(); return 'focus msg'; })()
