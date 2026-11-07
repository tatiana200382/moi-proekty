(() => {
  const links = [...document.querySelectorAll('a')].filter(a => /draftId=/.test(a.href)).map(a => a.href);
  return JSON.stringify([...new Set(links)].slice(0, 5), null, 1);
})()
