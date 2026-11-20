'use strict';
const statusRegion = document.getElementById('copy-status');
for (const button of document.querySelectorAll('[data-copy]')) {
 button.hidden = false;
 button.addEventListener('click', async () => {
  const text = document.getElementById(button.dataset.copy);
  const hint = button.closest('.prompt').querySelector('.copy-hint');
  try {
   if (!navigator.clipboard || !window.isSecureContext) throw new Error('Clipboard unavailable');
   await navigator.clipboard.writeText(text.innerText.trim());
   hint.textContent = 'Запрос скопирован. Вставьте его в чат вместе с указанными файлами.';
   statusRegion.textContent = 'Запрос скопирован.';
  } catch (_) {
   const range = document.createRange(); range.selectNodeContents(text);
   const selection = window.getSelection(); selection.removeAllRanges(); selection.addRange(range);
   hint.textContent = 'Автокопирование недоступно. Текст выделен: нажмите Ctrl+C или Cmd+C либо выберите «Копировать» в меню выделения.';
   statusRegion.textContent = 'Автокопирование недоступно. Скопируйте выделенный текст вручную.';
  }
 });
}
if ('IntersectionObserver' in window) {
 const links = [...document.querySelectorAll('.contents ol a')];
 const observer = new IntersectionObserver(entries => {
  const active = entries.filter(x => x.isIntersecting).sort((a,b) => a.boundingClientRect.top-b.boundingClientRect.top)[0];
  if (!active) return;
  for (const link of links) {
   if (link.hash === '#' + active.target.id) link.setAttribute('aria-current','step');
   else link.removeAttribute('aria-current');
  }
 }, {rootMargin:'0px 0px -65% 0px',threshold:0});
 document.querySelectorAll('.lesson .step[id]').forEach(h => observer.observe(h));
}
