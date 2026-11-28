# План: убрать старый цикл заявок с Мака

Дата: 28.11.2026. Разрешение владельца: «Убери».

## Что меняю

1. Удаляю login item `watch-sales.command` из «Элементов входа».
2. Останавливаю текущий цикл (PID 917) и его `sleep`, чтобы Терминал перестал работать сейчас.
3. Chrome 9224 не трогаю: он нужен `com.silversong.flowwow.keepalive`.

## Зачем

Старый цикл дублирует домашний сервер, держит Терминал и каждые 5 минут падает с `AVITO_OK`. Домашний сервер уже собирает Авито, ВК и Яндекс.

## До изменения

- Login items: Comet, Handy, Google Drive, watch-sales.command.
- Домашний сервер: cron `collect-all`, `sales_pipeline`, `max-inbox` активен; лог пишет `done`.
- PID 917 — `watch-sales.command`; Chrome 936 — headless.

## Проверка

- `osascript ... get name of every login item` — без `watch-sales.command`.
- `ps -p 917` — пусто.
- `watch.log` — новых записей нет.
- Домашний сервер продолжает собирать.
- Chrome 936 и CDP 9224 живы.

## Откат

Вернуть login item:

```bash
osascript -e 'tell application "System Events" to make login item at end with properties {path:"/Users/tatiana/Desktop/Обучение ИИ/proekty/Мои проекты/otdel-prodazh/tools/watch-sales.command", hidden:false}'
```

Запустить вручную: `open "/Users/tatiana/Desktop/Обучение ИИ/proekty/Мои проекты/otdel-prodazh/tools/watch-sales.command"`.

## Важно

После перезагрузки Chrome 9224 больше не стартует сам: раньше его поднимал этот цикл. Если Flowwow нужен на автопилоте — добавить отдельный автозапуск Chrome без цикла заявок.

## Результат (28.11, 04:36)

- Login item `watch-sales.command` удалён; остались Comet, Handy, Google Drive.
- Цикл PID 917 и `sleep 1780` остановлены; `watch.pid` удалён.
- Chrome 936 был в той же группе процессов и тоже погас. Перезапущен отдельно (PID 1994), CDP 9224 отвечает, открыта одна вкладка.
- Домашний сервер продолжает собирать: cron `collect-all`/`sales_pipeline`/`max-inbox`, лог `done`.
- Важно: после перезагрузки Chrome сам не стартует; если Flowwow нужен на автопилоте, нужен отдельный автозапуск Chrome без цикла заявок.
