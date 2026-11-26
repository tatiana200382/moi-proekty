# Сводка по инфраструктуре (актуально на 26.11.2026)

Один файл вместо 40 заметок. Подробные истории — в `arhiv/docs-2026-11-26/infra/`.

## Серверы

| Сервер | Адрес | Роль | Доступ |
|---|---|---|---|
| **Домашний** (`plex2`) | `ai.m-tik.com`, порт **222**, пользователь `tanya` | заявки, карточки, ответы клиентам, Playwright + Xvfb | через DE-прыжок; обёртка `~/bin/domashniy` |
| **Германия** (Hetzner) | `2.31.104.44` | xray VLESS+Reality **443**, nginx **8443** (DSH), squid **3128**, доктор | ключ `~/.ssh/id_ed25519_server` |
| **Россия** (HostKey) | `111.88.83.206` | realm **443** → Германия:443, squid **3128** | ключ `~/.ssh/id_ed25519_ru` |
| **Мак** | `188.242.157.159` | рабочий браузер, резерв | — |

## VPN

| Что | Значение |
|---|---|
| Профиль телефона | **Silversong-RU-RELAY** (`111.88.83.206:443`, Reality, SNI `www.bing.com`) |
| Выход телефона | Германия `2.31.104.44` |
| Ссылка и QR | `infra/vless-relay-ssylka.txt`, `infra/vless-relay-qr.png` |
| Прокси Мака | HTTP `127.0.0.1:8118` → Германия; SOCKS `1082` |
| Сон дисплея | launchd `ru.silversong.awake` (`caffeinate`) |

## Чат «Заявки» (MAX)

| Параметр | Значение |
|---|---|
| chat_id | `-81003587560055` |
| Бот | «Заявки SilwerSongFlowers», user_id `539752599` |
| Токен / сертификат | `~/.config/max-bot/token`, `agent-marketolog/bot/certs/max-ca.pem` |
| Ответ флориста | `<короткий номер заявки> <текст>` — работает для ВК, Авито, MAX |
| Яндекс | по номеру бот подсказывает телефон для звонка |

## Каналы и состояние (без Мака)

| Канал | Сбор | Ответ | Инструмент |
|---|---|---|---|
| Авито | ✅ | ✅ через `xvfb-run` | `avito-leads-server.py`, `avito-send-xvfb.py` |
| ВКонтакте | ✅ | ✅ | `vk-leads-server.py`, `vk-send-server.py` |
| MAX | ✅ | ✅ | `max-leads-server.py`, `max-inbox-server.py` |
| Яндекс.Карты | ✅ | звонок | `yandex-leads-server.py` |

## Расписание на `plex2` (crontab пользователя `tanya`)

```
*/5  … sales_pipeline.py --auto        # карточки в MAX
*/5  … max-leads-server.py             # входящие клиента в MAX
*/2  … max-inbox-server.py             # ответы флористов
*/10 … avito-leads-server.py           # сбор Авито
*/10 … vk-leads-server.py              # сбор ВК
*/10 … yandex-leads-server.py          # сбор Яндекса
*/5  … avito_check.py                  # проверка сессии Авито
```

## Правила заявок

| Правило | Значение |
|---|---|
| Заявки старше | **3 дня** — в чат не отправляются (`archived_old`) |
| Авито без телефона | готовность **B**, идёт в работу |
| Фильтр Авито | только объявления из `config.json → allow_item_titles` |
| Карточка | время · источник, клиент, «От клиента», «Наш ответ», «Магазин» (Яндекс), короткий номер |

## Доктор

| Параметр | Значение |
|---|---|
| Файл | `/opt/doktor/storozh.py` на Германии |
| Разрешённые службы | `dsh-web, nginx, xray, squid, ssh, fail2ban, cron, realm, mtg, hysteria` |
| Удалённые хосты | `/etc/doktor/hosts.json` → Россия (realm, squid, ssh) |

## Откаты

| Что | Где |
|---|---|
| Скрипты | `arhiv/bak-2026-11-26/` (22 файла `.bak`) |
| Заявки | `arhiv/leads-backup/*.tgz` |
| Профили xray | `/root/xray.json.bak-*` на Германии |
| nginx | `/etc/nginx/sites-available/default.bak-*` |

## Что удалено как устаревшее

| Что | Куда |
|---|---|
| Профили Hysteria2, WS, XHTTP, 2053 | `arhiv/docs-2026-11-26/infra/` |
| Фото-библиотека 40 МБ | `arhiv/media-2026-11-26/agent-foto/` |
| Архив сервера 11 МБ | `arhiv/media-2026-11-26/` |
