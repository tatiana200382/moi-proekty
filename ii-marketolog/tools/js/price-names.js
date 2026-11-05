(() => {
  const names = [];
  document.querySelectorAll('a, span, div').forEach((el) => {
    if (el.children.length === 0) {
      const t = el.textContent.trim();
      if (t.length > 3 && t.length < 60 && /[А-Яа-я]/.test(t) && !/^(Название|Цена|Категория|Описание|Товары и услуги|Данные актуальны|Загрузить XLS\/YML|Скачать прайс XLSX)/.test(t)) {
        if (/букет|Букет|Бекет|лизиантус|роза|Роз|корзин|коробк|шляп|сумочк|Океан|любить|Время/i.test(t)) names.push(t);
      }
    }
  });
  return JSON.stringify([...new Set(names)], null, 1);
})()
