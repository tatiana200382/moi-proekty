// Входящие сообщества ВКонтакте (/gim<id>) → диалоги.
// Ничего не открывает и не отправляет: только читает список.
(async () => {
  await new Promise((r) => setTimeout(r, 2500));
  const body = document.body.innerText;
  const enabled = !/разрешите сообщения/i.test(body);
  const items = [...document.querySelectorAll('[data-testid="vkme_convo_list_item"]')];
  return {
    url: location.href,
    title: document.title,
    collected_at: new Date().toISOString(),
    enabled,
    chats: items.map((el) => ({
      peer: el.getAttribute("data-peer-id") || "",
      text: el.innerText,
    })),
  };
})()
