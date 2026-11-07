(() => {
  const sels = [...document.querySelectorAll('select')].map((s,i)=>({i, opts:[...s.options].map(o=>o.text).slice(0,6)}));
  const btnTexts = [...document.querySelectorAll('button')].map(b=>(b.innerText||'').trim()).filter(Boolean).slice(0,12);
  const labels = [...document.querySelectorAll('label')].map(l=>(l.innerText||'').trim()).filter(Boolean).slice(0,12);
  return JSON.stringify({sels, btnTexts, labels, photos: document.body.innerText.match(/\d+ из 10/)?.[0]}, null, 1);
})()
