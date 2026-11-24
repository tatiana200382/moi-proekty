# Задание администратору: установка на Ubuntu (без доступа для нас)

Дата: 24.11.2026. Сервер `ai.m-tik.com`, Ubuntu 26.04. Админ всё делает сам, SSH нам не нужен.

## Что лежит рядом

| Файл | Что это |
|---|---|
| `silversong-server.tar.gz` | архив 11 МБ: скрипты, службы, установщик |
| `README-DLYA-ADMINA.txt` | инструкция внутри архива |

## Текст для администратора (можно копировать целиком)

---

Здравствуйте! Подготовили всё для установки, SSH-доступ нам не нужен — сделайте, пожалуйста, по шагам.

**1. Скачать архив и распаковать на сервере**

```
scp silversong-server.tar.gz root@ai.m-tik.com:/root/
ssh root@ai.m-tik.com
tar -xzf /root/silversong-server.tar.gz -C /root/
cd /root/silversong
```

**2. Запустить установку**

```
sudo bash INSTALL.sh
```

Скрипт сам поставит `python3`, `chromium`, `ufw`; создаст пользователя `silversong` и папку `/opt/silversong`; **запретит сон** сервера; включит три службы: чтение Авито/ВК каждые 15 минут, сторож `/health` на порту 8790, Chrome с отладочным портом; **закроет порт 11434** от интернета.

**3. Положить файлы доступа**

- токен бота MAX → `/opt/silversong/otdel-prodazh/runtime/max-bot/token` (пришлём отдельно);
- сертификат `max-ca.pem` → `/opt/silversong/max-ca.pem`;
- cookies Авито и ВК → `/opt/silversong/secrets/cookies.json` (загрузим вместе: на 10 минут откроете порт 9224 для нашего IP).

Затем:

```
chown -R silversong:silversong /opt/silversong
systemctl restart chrome-cdp silversong-health
systemctl start silversong-poll.service
```

**4. Прислать нам**

```
systemctl status silversong-poll.timer --no-pager | head -5
systemctl status silversong-health.service --no-pager | head -5
curl -s http://127.0.0.1:8790/health
tail -30 /opt/silversong/otdel-prodazh/runtime/logs/run.log
```

И ответить на три вопроса:

1. Это физический сервер или VPS?
2. Есть ли ИБП (бесперебойник)?
3. Внешний IP сервера — проверим сторож.

Заранее спасибо!

---

## Что делаем мы потом

| Шаг | Как |
|---|---|
| 1 | Проверим `http://IP:8790/health` — должно быть `{"ok": true}` |
| 2 | Загрузим cookies через порт 9224 (пока открыт для нашего IP) |
| 3 | Попросим тестовое сообщение в Авито |
| 4 | Убедимся, что карточка пришла в MAX |
| 5 | Попросим закрыть 9224 |

## Что мы НЕ просим

- SSH-доступ;
- открывать порт 11434 наружу;
- права публиковать что-либо в Авито (только чтение).

## Риски

| Риск | Что значит |
|---|---|
| Chromium как snap | на Ubuntu 24+ браузер ставится только snap — это нормально |
| Avito капча с серверного IP | возможно, потребуется разовая ручная проверка |
| Свет без ИБП | сервер выключится — заявки встанут |
| Cookies живут 1–3 месяца | вход нужно периодически обновлять |
