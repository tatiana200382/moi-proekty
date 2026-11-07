# Инструменты для Авито: разбор и выбор — 2026-11-07

Задача: найти на GitHub всё, что помогает работать с Авито, выбрать лучшее. Правило выбора — `../PRAVILA.md`.

Найдено 33 репозитория по запросам «avito api python», «avito autoload xml», «avito parser», «avito feed generator», «avito analytics». Ниже значимые.

## Кандидаты

| Репозиторий | ★ | Обновлён | Лицензия | Что делает | Вердикт |
|---|---:|---|---|---|---|
| [Duff89/parser_avito](https://github.com/Duff89/parser_avito) | 803 | 2026-09-30 | нет | парсер объявлений | **отклонён**: лицензии нет, парсинг против правил Авито, риск бана аккаунта |
| [Vladimir-Human/ru-marketplace-mcp](https://github.com/Vladimir-Human/ru-marketplace-mcp) | 182 | 2026-11-07 | MIT | MCP-сервер по 12 площадкам | отклонён: чтение чужих объявлений, у нас нет MCP-клиента под это |
| [DimaKalbfleysh/Avito](https://github.com/DimaKalbfleysh/Avito) | 83 | 2018-12-19 | нет | парсер с телефонами | отклонён: 8 лет без обновлений, лицензии нет |
| [Egor01KKK/avito-parser](https://github.com/Egor01KKK/avito-parser) | 29 | 2026-10-07 | нет | парсер поиска | отклонён по той же причине |
| [Case211/avito-watch](https://github.com/Case211/avito-watch) | 26 | 2026-10-31 | AGPL-3.0 | бот-следилка | отклонён: AGPL и не наша задача |
| [elchin92/avito-mcp](https://github.com/elchin92/avito-mcp) | 26 | 2026-11-03 | MIT | 148 инструментов: чаты, объявления, заказы, аналитика | **кандидат**: полезно, но нужен ключ API Авито и MCP-клиент; отложен |
| [mickberrad659-sketch/Avito-Parser](https://github.com/mickberrad659-sketch/Avito-Parser) | 24 | 2026-07-28 | нет | обход защиты | отклонён: обход защиты и лицензии нет |
| [18studio/avito_python_api](https://github.com/18studio/avito_python_api) | 9 | 2026-05-25 | MIT | SDK официального API | **кандидат**: пригодится, если получим ключ API |
| [sergeyvyalkov-dev/avito-sdk](https://github.com/sergeyvyalkov-dev/avito-sdk) | 1 | 2026-04-08 | MIT | SDK | отклонён: один автор, сырой |
| [kozandlov/avito-python-sdk](https://github.com/kozandlov/avito-python-sdk) | 1 | 2026-08-04 | AGPL-3.0 | async SDK | отклонён: AGPL |
| [Aleksey-Voko/Avito_autoload](https://github.com/Aleksey-Voko/Avito_autoload) | 5 | 2020-03-27 | MIT | генератор XML для Автозагрузки | отклонён как код, **взят как ориентир формата**: 6 лет без обновлений |
| [dub1401/AvitoAPI](https://github.com/dub1401/AvitoAPI) | 5 | 2024-07-23 | Apache-2.0 | API сайта | отклонён: старый, неофициальный |
| [maxRakh/python_avito_parser](https://github.com/maxRakh/python_avito_parser) | 18 | 2023-03-20 | нет | парсер + бот | отклонён: заброшен, лицензии нет |
| остальные (avito-autoload-feed, avito-feed и др.) | 0–2 | 2026 | нет | генераторы XML | отклонены: ноль звёзд, нет лицензий |

## Что выбрано

1. **Свой генератор XML для «Авито Автозагрузки»** — официальный способ управлять объявлениями: файл фида, который Авито сам забирает. Без парсинга, без бана, без чужих библиотек. Формат сверяю с документацией Авито, ориентир — `Aleksey-Voko/Avito_autoload`.
2. **Ручная работа через кабинет Авито** — там уже открыт доступ и видны объявления, сообщения и аналитика. Публикация и правка — с согласия владельца.
3. **Ключ API Авито** — если владелец его получит, подключаем `elchin92/avito-mcp` или `18studio/avito_python_api`. Пока ключа нет, оба лежат в резерве.

## Чего не делаем

- Не парсим чужие объявления: это нарушение правил Авито и риск блокировки аккаунта магазина. Конкурентов смотрим глазами в браузере, вручную и в малом объёме.
- Не берём AGPL-код в свои инструменты.
- Не ставим библиотеки без лицензии и свежих коммитов.

## Проверка

Генератор фида: `tools/avito-feed.py` — собирает XML из таблицы товаров, пишет в `results/avito-feed.xml`. Первый прогон — на 3 позициях, чтобы проверить формат.
