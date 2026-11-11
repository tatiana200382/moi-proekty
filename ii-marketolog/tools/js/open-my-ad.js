(() => { const a=[...document.querySelectorAll('a')].find(x=>/8404314990/.test(x.href) && /rasteniya/.test(x.href)); if(!a) return 'нет ссылки'; a.click(); return 'открыл'; })()
