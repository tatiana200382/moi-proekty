(() => {
  const sels=[...document.querySelectorAll('select')];
  const info=sels.map((s,i)=>({i, opts:[...s.options].slice(0,4).map(o=>o.text), count:s.options.length, multi:s.multiple}));
  return JSON.stringify(info.slice(0,6));
})()
