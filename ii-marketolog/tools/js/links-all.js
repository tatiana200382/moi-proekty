(() => [...document.querySelectorAll('a')].map(a=>({t:(a.innerText||'').trim().slice(0,40), h:a.href})).filter(x=>x.t || /api|automation/.test(x.h)).slice(0,15))()
