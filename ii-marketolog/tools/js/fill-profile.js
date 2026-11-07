(() => {
  const t = document.body.innerText.replace(/\n{2,}/g,'\n');
  const btns = [...document.querySelectorAll('button')].map(b=>b.innerText.trim()).filter(t=>t && t.length<40);
  return JSON.stringify({
    head: t.slice(0, 400),
    hasWizard: /Заполните|Профиль|Подтверд|Проверьте/i.test(t),
    buttons: [...new Set(btns)].slice(0,20),
    alerts: (t.match(/[^\n]*(Обновите|Подтвердите|Заполните|Проверьте)[^\n]*/g)||[]).slice(0,6)
  }, null, 1);
})()
