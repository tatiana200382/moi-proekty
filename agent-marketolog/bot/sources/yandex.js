// Заявки из кабинета Яндекс.Бизнеса → сырые строки таблицы.
// Ничего не нажимает: читает только видимые строки списка заявок.
(() => {
  const rows = [...document.querySelectorAll(".ya-business-ui-table__row_type_body")];
  return {
    url: location.href,
    title: document.title,
    collected_at: new Date().toISOString(),
    rows: rows
      .map((row) => ({
        cells: [...row.querySelectorAll(".ya-business-ui-table__cell")].map((c) => c.innerText.trim()),
      }))
      .filter((r) => r.cells.length >= 4),
  };
})()
