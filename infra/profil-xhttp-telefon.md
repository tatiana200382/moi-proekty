# Профиль XHTTP для телефона (по образцу рабочего Алматы)

Дата: 25.11.2026, 23:20.

## Почему такой вариант

| Факт | Значение |
|---|---|
| Алматы в Happ | ✅ работает — транспорт **xhttp + Reality** |
| Наш TCP+Reality на 443 | ❌ подключается, данные не идут |
| Вывод | оператор режет именно **TCP+Reality**, а xhttp проходит |

## Что настроено на немецком сервере

| Компонент | Значение |
|---|---|
| XHTTP-вход xray | `127.0.0.1:10086`, путь `/xhttp` (только локально) |
| nginx 8443 (TLS, HTTP/2) | проксирует `/xhttp` → `127.0.0.1:10086`, без basic-auth |
| Сертификат | Let's Encrypt `2-31-104-44.sslip.io` ✅ |
| Рабочий 443/VLESS-Reality | **не тронут** |

## Изолированный тест (с российского сервера)

| Проверка | Результат |
|---|---|
| Выходной IP через XHTTP | **2.31.104.44** ✅ |
| Код | **200** ✅ |
| Логи nginx | POST/GET `/xhttp/...` **HTTP/2** → 200 (выглядит как обычный сайт) |

## Параметры профиля

| Параметр | Значение |
|---|---|
| Адрес | `2.31.104.44` |
| Порт | **8443** |
| UUID | `09c0a817-32d4-4103-a201-1d1446d0cd88` |
| Транспорт | **xhttp** |
| TLS | да, SNI `2-31-104-44.sslip.io` |
| Путь | `/xhttp` |
| Host | `2-31-104-44.sslip.io` |

## Ссылка

```
vless://09c0a817-32d4-4103-a201-1d1446d0cd88@2.31.104.44:8443?encryption=none&security=tls&sni=2-31-104-44.sslip.io&fp=chrome&type=xhttp&path=%2Fxhttp&host=2-31-104-44.sslip.io&mode=auto#Silversong-XHTTP
```

QR: `infra/vless-xhttp-qr.png`

## Откат (если не понадобится)

| Шаг | Команда |
|---|---|
| Конфиг nginx | `cp /etc/nginx/sites-available/dsh-server.bak-xhttp /etc/nginx/sites-available/dsh-server && systemctl reload nginx` |
| Конфиг xray | `cp /root/xray.json.bak-xhttp /root/xray.json && systemctl restart xray` |

## Если и это не сработает

| Гипотеза | Действие |
|---|---|
| Оператор режет и 8443 | перенести XHTTP на **443 через nginx stream** (SNI-роутинг) |
| Нужен другой протокол | **Hysteria2 (UDP 443)** |
