# UTM-разметка: таблица ссылок

Задача — чтобы Дана могла сказать, откуда пришла заявка. Сейчас разметки нет, поэтому отчёт по каналам строится на догадках.

## Схема

`utm_source` — площадка, `utm_medium` — тип размещения, `utm_campaign` — повод или месяц, `utm_content` — конкретный материал.

| Параметр | Значения |
|---|---|
| source | `yandex_maps`, `vk`, `avito`, `flowwow`, `telegram`, `site`, `b2b` |
| medium | `card`, `post`, `story`, `listing`, `message`, `email` |
| campaign | `2026-11`, `8marta-2027`, `den-materi-2026` |
| content | `buket-dnya`, `foto-do-otpravki`, `price-3850` |

## Готовые ссылки

| Куда | Ссылка |
|---|---|
| Карта Белышева → сайт | `https://kladovaja-tsvetov-ssflowers.clients.site/?utm_source=yandex_maps&utm_medium=card&utm_campaign=2026-11&utm_content=belysheva` |
| Карта Трибуца → сайт | `https://kladovaja-tsvetov-ssflowers.clients.site/?utm_source=yandex_maps&utm_medium=card&utm_campaign=2026-11&utm_content=tribuca` |
| Карта Ленинский → сайт | `https://kladovaja-tsvetov-ssflowers.clients.site/?utm_source=yandex_maps&utm_medium=card&utm_campaign=2026-11&utm_content=leninsky` |
| Пост ВК → сайт | `https://kladovaja-tsvetov-ssflowers.clients.site/?utm_source=vk&utm_medium=post&utm_campaign=2026-11&utm_content=<название>` |
| Объявление Авито → сайт | `https://kladovaja-tsvetov-ssflowers.clients.site/?utm_source=avito&utm_medium=listing&utm_campaign=2026-11&utm_content=buket-3850` |
| Telegram → сайт | `https://kladovaja-tsvetov-ssflowers.clients.site/?utm_source=telegram&utm_medium=post&utm_campaign=2026-11&utm_content=<название>` |

## Правила

1. Одна ссылка — один материал. Не переиспользовать ссылку с другим `utm_content`.
2. Нижний регистр, латиница, дефисы вместо пробелов.
3. Не ставить UTM на внутренние ссылки сайта — только на вход извне.
4. Ссылки для B2B-письма — `utm_source=b2b&utm_medium=email`.
5. Ссылку с UTM не сокращать через сторонние сервисы: теряется источник.

## Что это даёт

- Дана видит переходы по каналам в Метрике, а не «примерно».
- Через 7 дней после внедрения появляется первый честный отчёт по переходам.
- Пока Метрика не подключена, UTM всё равно фиксируются в журнале обращений (поле «откуда»).

## Ограничение

UTM показывает переход, но не звонок. Для звонков нужен подменный номер (коллтрекинг) или вопрос «как вы нас нашли?» при каждом заказе. Первый шаг дешевле — вопрос на кассе.
