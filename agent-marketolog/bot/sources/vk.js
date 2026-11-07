// Сообщения сообщества ВКонтакте → состояние и список диалогов.
// Только чтение. Пока в сообществе не включены сообщения, вернёт enabled: false.
(() => {
  const body = document.body.innerText;
  const enabled = !/разрешите сообщения/i.test(body);
  const items = [...document.querySelectorAll('[data-testid="vkme_convo_list_item"]')];
  return {
    url: location.href,
    title: document.title,
    collected_at: new Date().toISOString(),
    enabled,
    chats: items.map((el) => ({
      text: el.innerText.replace(/\n+/g, " | ").slice(0, 300),
      unread: (el.querySelector('[data-testid="vkme_convo_list_item_unread_counter"]') || {}).innerText || "",
    })),
  };
})()
