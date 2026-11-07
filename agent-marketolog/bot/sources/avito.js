// Список чатов в мессенджере Авито → сырые строки.
// Ничего не открывает и не отправляет. Фильтр по объявлениям — на стороне Python.
(() => {
  const links = [...document.querySelectorAll('[data-marker="channels/channelLink"]')];
  const text = (root, marker) => {
    const el = root.querySelector(`[data-marker="${marker}"]`);
    return el ? el.innerText.trim() : "";
  };
  const chats = links.map((link) => {
    const row = link.closest('[data-marker="channels/channel"]') || link.parentElement;
    return {
      href: link.getAttribute("href") || "",
      user: row ? text(row, "channels/user-title") : "",
      item: row ? text(row, "channels/item-title") : "",
      price: row ? text(row, "channels/item-price") : "",
      last: row ? text(row, "channels/last-message") : "",
      row_text: row ? row.innerText.replace(/\n+/g, " | ").slice(0, 300) : "",
    };
  });
  return {
    url: location.href,
    title: document.title,
    collected_at: new Date().toISOString(),
    logged_in: !/Войти|войдите/i.test(document.title),
    chats,
  };
})()
