(() => {
  const dlg = document.querySelector('[role=dialog]') || document.querySelector('[class*=Modal]');
  const txt = (dlg ? dlg.innerText : document.body.innerText).replace(/\n{2,}/g,'\n');
  const opts = [...document.querySelectorAll('[role=dialog] *')].filter(e=>e.children.length===0 && e.textContent.trim().length<30 && e.textContent.trim().length>1).map(e=>e.textContent.trim());
  return JSON.stringify({ modal: !!dlg, text: txt.slice(0, 600), options: [...new Set(opts)].slice(0, 25) }, null, 1);
})()
