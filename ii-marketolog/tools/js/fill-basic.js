(() => {
  const out = [];
  // 1. вид объявления
  const s = document.querySelectorAll('select')[0];
  if (s) {
    const opt = [...s.options].find(o => o.text.trim() === 'Товар приобретён на продажу');
    if (opt) {
      const set = Object.getOwnPropertyDescriptor(HTMLSelectElement.prototype, 'value').set;
      set.call(s, opt.value); s.dispatchEvent(new Event('change', {bubbles:true}));
      out.push('вид: ' + opt.text.trim());
    }
  }
  // 2. цена: input рядом с словом «Цена»
  const all = [...document.querySelectorAll('input')];
  const priceInput = all.find(i => {
    const ctx = (i.closest('div')?.parentElement?.innerText || '').toLowerCase();
    return ctx.includes('цена') && ctx.length < 120;
  });
  if (priceInput) {
    const set = Object.getOwnPropertyDescriptor(HTMLInputElement.prototype, 'value').set;
    set.call(priceInput, '1950');
    priceInput.dispatchEvent(new Event('input', {bubbles:true}));
    out.push('цена: 1950');
  } else out.push('поле цены не найдено');
  // 3. описание
  const ta = [...document.querySelectorAll('textarea')].find(t => {
    const ctx = (t.closest('div')?.parentElement?.innerText || '').toLowerCase();
    return ctx.includes('описание');
  });
  if (ta) {
    const set = Object.getOwnPropertyDescriptor(HTMLTextAreaElement.prototype, 'value').set;
    set.call(ta, "Букет под ваш повод, а не «как на картинке».\n\nСвидание, день рождения, извиниться, поздравить маму или коллегу — скажите повод, дату и бюджет, предложим 2–3 варианта.\n\nКак покупаете:\n1. Пишете: повод, когда нужно, бюджет.\n2. Собираем и присылаем фото до отправки.\n3. При получении проверяете — если что-то не так, заменим на месте.\n\nЦены по прайсу:\n— Букет с розами в сумочке — 1 950 ₽\n— Букет дня — 4 350 ₽\n— Букет белых роз 80 см — 11 000 ₽\nНа фото — пример букета; соберём вариант под ваш бюджет.\n\nЗабрать или доставка по Санкт-Петербургу:\n— Адмирала Трибуца, 8 — круглосуточно\n— Ленинский проспект, 56 — круглосуточно\n— Белышева, 5/6 — с 9:00 до 22:00\n\nВ каждом букете памятка по уходу.\n\nРейтинги в Яндекс.Картах на 7 ноября: 5,0 (Белышева), 4,9 (Трибуца), 4,5 (Ленинский).\n\nНапишите повод и бюджет — ответим в рабочее время.");
    ta.dispatchEvent(new Event('input', {bubbles:true}));
    out.push('описание: заполнено');
  } else out.push('поле описания не найдено');
  return JSON.stringify(out);
})()
