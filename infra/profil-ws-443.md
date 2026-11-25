# Профиль VLESS через WebSocket за nginx на 443

Дата: 25.11.2026, 23:55. Вариант A плана, **по разрешению владельца**.

## Что изменено

| Что | Было | Стало |
|---|---|---|
| Порт **443** | xray (Reality) | **nginx** (TLS + HTTP/2), обычный сайт `200 OK` |
| Reality | на 443 | **на 2053** |
| Туннель для телефона | Reality на 443 | **WebSocket `/ws`** → xray `127.0.0.1:10087` |
| Сайт DSH на 8443 | работает | **не тронут** |

## Изолированный тест (с российского сервера)

| Проверка | Результат |
|---|---|
| Выходной IP через WS | **2.31.104.44** ✅ |
| `telegram.org` | **200** ✅ |
| Скачивание 10 МБ | ✅ 10 485 760 байт за **1,92 с** (~5,4 МБ/с) |

## Параметры профиля

| Параметр | Значение |
|---|---|
| Адрес | `2.31.104.44` |
| Порт | **443** |
| UUID | `586d710a-3cf9-42b3-a044-7f3e49ca90fe` |
| Транспорт | **ws (WebSocket)** |
| TLS | да, SNI `2-31-104-44.sslip.io` |
| Путь | `/ws` |
| Host | `2-31-104-44.sslip.io` |

## Ссылка

```
vless://586d710a-3cf9-42b3-a044-7f3e49ca90fe@2.31.104.44:443?encryption=none&security=tls&sni=2-31-104-44.sslip.io&fp=chrome&type=ws&path=%2Fws&host=2-31-104-44.sslip.io#Silversong-WS
```

QR: `infra/vless-ws-qr.png`

## Важно

| Что | Значение |
|---|---|
| Старый профиль **Silversong-443** (Reality) | ❌ больше не работает — Reality переехал на 2053 |
| Reality на 2053 | ✅ работает (для других устройств, если понадобится) |

## Откат (полный, 1 минута)

```
cp /root/xray.json.bak-ws /root/xray.json
rm -f /etc/nginx/sites-enabled/vless-ws
systemctl restart xray
systemctl reload nginx
```
