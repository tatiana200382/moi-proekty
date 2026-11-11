(() => { const i=[...document.querySelectorAll('input')].find(x=>(x.placeholder||'').includes('видите только вы')); if(!i) return 'нет'; i.focus(); return 'focus name'; })()
