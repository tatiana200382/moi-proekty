# Решение по схеме «промежуточный сервер»: вход в России, выход в Германии

Дата: 25.11.2026, 23:52. Найдено по документации:
[meridian relay](https://github.com/getmeridian/meridian/blob/211e95a6472b6a4f72fb2dde1b4cc692614ded4b/website/src/content/docs/ru/relay.md) — «промежуточный сервер (relay) создаёт точку входа на российском IP, который блокируют гораздо реже».

## Схема

```
Телефон → российский сервер 111.88.83.206:443 (Realm) → немецкий 2.31.104.44:2053 (Reality) → интернет
```

| Что видит оператор | Что видит сайт |
|---|---|
| соединение с **российским** адресом | **2.31.104.44** (Германия) |

Шифрование сквозное: российский сервер видит только зашифрованный поток и **не расшифровывает**.

## Что сделано на российском сервере

| Компонент | Значение |
|---|---|
| `realm` 2.9.6 | `/usr/local/bin/realm` |
| Конфиг | `/etc/realm.toml` (listen `0.0.0.0:443` → `2.31.104.44:2053`) |
| Служба | `realm.service` — **active** |
| ufw | 443/tcp открыт |
| Squid 3128 | не тронут |

## Проверка с Мака (не с телефона)

| Проверка | Результат |
|---|---|
| Выходной IP через цепочку | **2.31.104.44** ✅ Германия |
| `telegram.org` | **200** ✅ |

## Профиль для телефона

| Параметр | Значение |
|---|---|
| Адрес | **111.88.83.206** (Россия) |
| Порт | 443 |
| UUID | `9a5e3986-c68b-4402-8f9b-fdbefed0bed5` |
| Reality | SNI `www.bing.com`, pbk `wId7ILUahRAQZ7q-xgtGAaWcp3svK4BtF9nLK-EhtyI`, sid `487738a453637e93` |
| Flow | `xtls-rprx-vision` |
| Выход | Германия |

Ссылка: `infra/vless-relay-ssylka.txt`, QR: `infra/vless-relay-qr.png`

## Откат

```
systemctl disable --now realm
ufw delete allow 443/tcp
rm -f /etc/systemd/system/realm.service /etc/realm.toml /usr/local/bin/realm
```
