# План: добавить Эвотор в исключения прокси

Дата: 28.11.2026. Разрешение владельца: «Добавь сайт Эватора в список исключений, которые ходят через Россию».

## Что меняю

Добавляю в обход системного прокси Wi-Fi:
- `evotor.ru`
- `*.evotor.ru` (личный кабинет, market, support)
- `эвотор.рф` — punycode `xn--b1ayaii7d.xn--p1ai`
- `*.xn--b1ayaii7d.xn--p1ai`

`evotor.com` не добавляю: это parked-домен «for sale», не сайт Эвотора.

## Зачем

Сайт и кабинет Эвотора должны видеть российский IP, а не немецкий.

## До изменения

- 71 запись в списке.
- Резервная копия: `plany/2026-11-28-proksi-bypass-before-evotor.txt`.
- `market.evotor.ru` открывается и напрямую (185.170.207.146), и через прокси (200); добавляю по просьбе для российского IP.

## Проверка

- `networksetup -getproxybypassdomains Wi-Fi` — 75 записей, есть evotor и punycode.
- `scutil --proxy` — записи видны.
- Chrome: `https://market.evotor.ru` открывается, заголовок «Эвотор».
- Остальной трафик по-прежнему через Германию.

## Откат

```bash
DOMAINS=()
while IFS= read -r d; do [ -n "$d" ] && DOMAINS+=("$d"); done < plany/2026-11-28-proksi-bypass-before-evotor.txt
networksetup -setproxybypassdomains Wi-Fi "${DOMAINS[@]}"
```

## Результат (28.11, 13:50)

- Список: 75 записей; добавлены `evotor.ru`, `*.evotor.ru`, `эвотор.рф` и его поддомены.
- Chrome: `https://market.evotor.ru` открылся, заголовок «Эвотор | Магазин приложений».
- Документ и XHR шли на `185.170.207.146` — напрямую, не через прокси.
- `evotor.com` не добавлял: parked-домен «for sale».
