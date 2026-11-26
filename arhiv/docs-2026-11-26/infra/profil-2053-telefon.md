# Новый тестовый профиль для телефона: порт 2053

Дата: 25.11.2026, 22:57. Выполнено **по разрешению владельца**.

## Что сделано

| Шаг | Результат |
|---|---|
| Резервная копия конфига | `/root/xray.json.bak-2026-11-25` ✅ |
| Второй вход VLESS+Reality на **2053** | добавлен ✅ |
| `xray -test` | **Configuration OK** ✅ |
| Порт 2053 в ufw | открыт ✅ |
| Рабочий **443** | ✅ **не тронут**, слушает |
| Перезапуск xray | active ✅ |

## Параметры профиля

| Параметр | Значение |
|---|---|
| Адрес | `2.31.104.44` |
| Порт | **2053** |
| UUID | `86ccd6d1-3a22-48d5-85b4-7de76a7a227d` |
| SNI | `www.bing.com` |
| Public key | `wId7ILUahRAQZ7q-xgtGAaWcp3svK4BtF9nLK-EhtyI` |
| Short ID | `ed3fa4ff167066f3` |
| Flow | **нет** (в отличие от 443) |
| Отпечаток | `chrome` |

## Изолированный тест (с российского сервера, не с телефона)

| Проверка | Результат |
|---|---|
| Выходной IP | **2.31.104.44** ✅ |
| `telegram.org` | **200** ✅ |
| Скачивание 10 МБ | ✅ 10 485 760 байт, ~197 КБ/с |

## Ссылка

```
vless://86ccd6d1-3a22-48d5-85b4-7de76a7a227d@2.31.104.44:2053?encryption=none&security=reality&sni=www.bing.com&fp=chrome&pbk=wId7ILUahRAQZ7q-xgtGAaWcp3svK4BtF9nLK-EhtyI&sid=ed3fa4ff167066f3&type=tcp#Silversong-2053
```

QR: `infra/vless-2053-qr.png`

## Откат (минута)

```
cp /root/xray.json.bak-2026-11-25 /root/xray.json
ufw delete allow 2053/tcp
systemctl restart xray
```

## Что дальше

| № | Проверка на телефоне | Ожидание |
|---|---|---|
| 1 | Импортировать **Silversong-2053** (QR) | профиль появился |
| 2 | Подключиться | знак VPN |
| 3 | `2ip.ru` в Safari | **Германия** |
| 4 | Telegram | грузится |
