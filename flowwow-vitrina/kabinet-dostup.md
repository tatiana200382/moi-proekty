# Кабинет продавца Flowwow: как Вова заходит сам

Проверено 25.11.2026. Владелец вошёл один раз, дальше агент открывает кабинет сам.

## Команды

```bash
cd flowwow-vitrina
node tools/flowwow-auth.mjs open    # восстановить сессию и открыть кабинет
node tools/flowwow-auth.mjs check   # проверить: кабинет открыт или закрыт
node tools/flowwow-auth.mjs save    # пересохранить куки (когда владелец снова вошёл)
node tools/flowwow-auth.mjs restore # только вернуть куки, без проверки
```

## Где лежит сессия

- Куки: `~/.config/flowwow/cookies.json`, права `600`, вне проекта.
- В git, в чат и в отчёты **не попадают**.
- Куки берутся из управляемого Chrome (CDP 9224) и возвращаются в него же.

## Как работать внутри

1. `open` → открывается `https://flowwow.com/admin/profile/shop/`.
2. Дальше ходить **только по меню кабинета** и по проверенным адресам:
   - `/admin/dashboard` — дашборд;
   - `/admin/profile/shop/` — профиль магазина;
   - `/admin/profile/delivery?shop_id=207627&tab=couriers` — доставка.
3. **Угаданные адреса не работают:** `/admin/orders` → «Unknown error», `/admin/products` → 404. Такие разделы открывать кликом по меню.

## Признак, что сессия потеряна

Вместо кабинета открывается клиентский сайт с окном «Укажите адрес доставки», город Москва. Лечение: `node tools/flowwow-auth.mjs open`.

## Ограничения

- Куки живут ограниченное время; когда истекут — нужен один вход владельца и `save`.
- Пароль агент не запрашивает и не хранит.
- Магазин: SilverSong Flowers, ID **207627**, статус «Открыт».

## Что проверено

| Проверка | Результат |
|---|---|
| `save` | 46 куки сохранены |
| `restore` | 46 куки восстановлены |
| `check` | «кабинет продавца ОТКРЫТ» |
| `open` | кабинет открылся на `/admin/profile/shop/` |
| Прямой `/admin/dashboard` | открывается, видны разделы и рейтинг магазина |
| Прямой `/admin/orders` | ошибка — только через меню |

## Автономный вход без владельца

Три уровня, от дешёвого к надёжному. Все проверены 25.11.2026.

### Уровень 1. Автообновление сессии (работает сейчас)

`tools/flowwow-keepalive.mjs` — каждые 6 часов: проверяет кабинет, обновляет куки, при обрыве восстанавливает их из файла.

Запускается агентом macOS (LaunchAgent):

```
~/Library/LaunchAgents/com.silversong.flowwow.keepalive.plist
```

Проверка: `launchctl print gui/$(id -u)/com.silversong.flowwow.keepalive | grep -E "state|runs"`, лог — `~/.config/flowwow/keepalive.log`.

Откат (выключить навсегда):

```bash
launchctl bootout gui/$(id -u)/com.silversong.flowwow.keepalive
rm ~/Library/LaunchAgents/com.silversong.flowwow.keepalive.plist
```

### Уровень 2. Автовход по паролю из Связки ключей

Нужен, когда серверная сессия всё-таки истечёт. Пароль хранит macOS, а не проект.

Один раз, в терминале (пароль вводится интерактивно и в чат не попадает):

```bash
security add-generic-password -s flowwow-seller -a "<почта>" -w
```

Дальше вход выполняется сам:

```bash
node tools/flowwow-login.mjs
```

Скрипт берёт логин и пароль из Keychain, открывает окно входа и заполняет поля.
Пароль в коде, в git и в логах не хранится.

Посмотреть, есть ли уже запись (без вывода пароля): `security find-generic-password -s flowwow-seller -a "<почта>" >/dev/null && echo есть`.

Удалить запись: `security delete-generic-password -s flowwow-seller`.

### Уровень 3. API-токен (совсем без браузера)

В кабинете: «Профиль» → «API-интеграция». Токен даёт доступ к заказам и товарам без входа в браузер.
Токен хранить в `~/.config/flowwow/api-token` (права 600), в проект и чат не копировать.

## Что проверено 25.11.2026

| Проверка | Результат |
|---|---|
| `flowwow-keepalive.mjs` вручную | «сессия открыта, куки обновлены» |
| LaunchAgent установлен | state = running, runs = 2 |
| Запуск из launchd | записи в `keepalive.log` появились |
| Минимальное окружение (`env -i`) | работает, выход 0 |
| `flowwow-login.mjs` | создан, ждёт записи пароля в Связке ключей |
