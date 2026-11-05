(() => {
  const t = document.body.innerText;
  const idx = t.toLowerCase().indexOf('актуальн');
  const checks = [...document.querySelectorAll('input[type=checkbox]')].map((c) => ({
    checked: c.checked,
    label: (c.closest('label')?.innerText || c.parentElement?.innerText || '').replace(/\n+/g, ' ').slice(0, 80),
  }));
  return JSON.stringify({
    around: idx >= 0 ? t.slice(Math.max(0, idx - 200), idx + 250).replace(/\n+/g, ' | ') : 'нет слова «актуальн»',
    checkboxes: checks.slice(0, 8),
  }, null, 1);
})()
