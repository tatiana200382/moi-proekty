# API Flowwow: доступ без браузера

Настроено 25.11.2026. Самый надёжный путь автономной работы: ни сессии, ни капчи.

## Токен

- Создан в кабинете: «Профиль» → «API-интеграция» → «Создать токен».
- Хранится: `~/.config/flowwow/token`, права `600`, вне проекта.
- В git, чат и отчёты не попадает. В отчётах печатать только маску вида `UX8w…4t9`.

## Что проверено

| Команда | Результат |
|---|---|
| `node tools/flowwow-api.mjs ping` | `{"say":"hello"}` |
| `node tools/flowwow-api.mjs shops` | магазин SilverSong Flowers, `shopId 50582`, статус `active`, адрес Ленинский 56 |
| `node tools/flowwow-api.mjs products 50582 --stats` | 95 товаров, из них активных 33 |
| `node tools/flowwow-api.mjs reviews 50582` | 28 отзывов, первый по дате — июнь 2026 |
| `/apiseller/orders` | 404 — эндпоинт заказов другой, ищем в документации |

## Важно: чего API не отдаёт

В ответе `products` **нет полей просмотров и покупок** — `withStats` их не добавляет. Поэтому «0 просмотров» из API означает «данных нет», а не «трафика нет». Просмотры смотреть только в кабинете или в приложении.

Также расходятся числа: API отдаёт 95 товаров и 33 активных, кабинет — 393 и 88. Причина не установлена; смотреть кабинет как основной источник.

## Команды

```bash
cd flowwow-vitrina
node tools/flowwow-api.mjs ping
node tools/flowwow-api.mjs shops
node tools/flowwow-api.mjs products 50582 --stats
node tools/flowwow-api.mjs reviews 50582
node tools/flowwow-api.mjs stocks 50582 <offerId...>
```

## Документация

Ссылка «Документация API» есть в кабинете на странице API-интеграции, а также Telegram-канал API.
