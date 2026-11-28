# План: исключения прокси — Яндекс, Госуслуги, Ростелеком, госсайты

Дата: 28.11.2026. Разрешение владельца: прямая просьба «Добавь в исключение напрямую без Германии…» — есть.

## Что меняю

Список обхода системного прокси Wi-Fi (HTTP/HTTPS/SOCKS). Добавляю:
- Яндекс: `yandex.ru`, `yandex.com`, `ya.ru`, `yandex.net`, `yandexcloud.net`, `yandex.cloud`, `yastatic.net`, `yandex.st`, `dzen.ru`, `kinopoisk.ru` и их поддомены.
- Госуслуги: `gosuslugi.ru`, `gu.spb.ru`.
- Ростелеком: `rt.ru`, `rostelecom.ru`.
- Госсайты: `gov.ru`, `government.ru`, `kremlin.ru`, `gov.spb.ru`, `mos.ru`, `mosreg.ru`, `nalog.ru`, `mvd.ru`, `gibdd.ru`, `mil.ru`, `sudrf.ru`, `мвд.рф` и основные порталы на `gov.ru`.

Полный список — `plany/2026-11-28-proksi-bypass.txt`.

## Зачем

Эти сайты должны видеть российский IP, а не немецкий `2.31.104.44`: иначе кабинеты, госуслуги и оплата работают неправильно или блокируются.

## До изменения

`networksetup -getproxybypassdomains Wi-Fi` — 11 записей. Копия: `plany/2026-11-28-proksi-bypass-backup.txt`.

## Изолированная проверка

Механизм исключений проверен 25.11 на `ipinfo.io` (Chrome показал российский IP). После изменения проверяю `https://yandex.ru/internet` в Chrome: IP должен быть российским, не `2.31.104.44`.

## Откат

```bash
networksetup -setproxybypassdomains Wi-Fi \
  "*.avito.ru" "avito.ru" "*.vk.com" "vk.com" "*.max.ru" "*.mail.ru" \
  "localhost" "127.0.0.1" "*.local" "flowwow.com" "*.flowwow.com"
```

Или из файла `plany/2026-11-28-proksi-bypass-backup.txt`.

## Риски

`*.yandex.ru` и `*.gov.ru` — широкие, но это и нужно. Если конкретный сайт перестанет открываться напрямую — убрать его домен и проверить снова; откат одной командой.

## Результат (28.11, 04:00)

- Применено: 71 запись, прокси HTTP/HTTPS/SOCKS остались включены.
- Chrome: `yandex.ru/internet` → `188.242.157.159`, Санкт-Петербург; контроль `api.ipify.org` → `2.31.104.44` (Германия).
- `spb.rt.ru` открылся; `www.gosuslugi.ru` показал российский IP, но страницу ошибки (вероятно, headless-браузер).
- Откат: `plany/2026-11-28-proksi-bypass-backup.txt`.
