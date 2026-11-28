# План: автозапуск Chrome для Flowwow

Дата: 28.11.2026. Разрешение владельца: «Google на автопилоте нужен для Flowwow, чтобы они могли работать автономно» (Chrome).

## Что делаю

Создаю LaunchAgent `ru.silversong.chrome-cdp`:
- запускает headless Chrome на порту **9224**;
- профиль `.chrome-profile` проекта;
- `RunAtLoad`, перезапуск только при аварийном выходе;
- без окна и без Терминала.

## Зачем

После удаления `watch-sales.command` старый цикл больше не поднимает Chrome. `Flowwow-keepalive` работает через CDP 9224 — без Chrome он не сможет поддерживать сессию.

## До изменения

- Chrome запущен вручную, PID 1994.
- LaunchAgent с таким именем нет.
- Login items: только Google Drive.

## Проверка

- `plutil -lint` — без ошибок.
- Остановить ручной Chrome, загрузить агент, `curl 127.0.0.1:9224/json/version` — отвечает.
- `launchctl print` — служба running, Chrome под launchd.
- `launchctl kickstart -k` — Chrome перезапускается, CDP снова отвечает.

## Откат

```bash
launchctl bootout gui/$(id -u)/ru.silversong.chrome-cdp
rm ~/Library/LaunchAgents/ru.silversong.chrome-cdp.plist
```

При необходимости запустить Chrome вручную тем же способом.

## Результат (28.11, 04:50)

- `plutil -lint` — OK, LaunchAgent загружен.
- Chrome под launchd, PID 2624; CDP 9224 отвечает.
- `kickstart -k`: PID 2563 → 2624, служба снова running.
- Память с Handy и Chrome — 14 ГБ занято, ~1,4 ГБ свободно; своп 0.
