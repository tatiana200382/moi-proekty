# План: разгрузить память Мака

Дата: 28.11.2026. Разрешение владельца: «Делай то, что нужно».

## Что меняю

1. Убираю Comet и Handy из «Элементов входа».
2. Закрываю Handy (он держит микрофон); Comet сейчас не запущен.
3. Останавливаю голосовой Python `tts_server.py` после озвучки.
4. Chrome 9224 не трогаю — он нужен `Flowwow-keepalive`.

## Зачем

Освободить ~2 ГБ, убрать постоянный микрофон и лишний браузер из автозапуска.

## До изменения

- Login items: Comet, Handy, Google Drive.
- Память: 15 ГБ занято, ~0,7 ГБ свободно, своп 0.
- Handy: два процесса, ~0,5 ГБ, микрофон.
- TTS: Python `tts_server.py`, ~1 ГБ.

## Проверка

- Login items без Comet и Handy.
- Процессов Handy и `tts_server.py` нет.
- Chrome 9224 и CDP живы.
- `top`/`vm_stat`/`swapusage` после.

## Откат

Вернуть автозапуск:

```bash
osascript -e 'tell application "System Events" to make login item at end with properties {path:"/Applications/Comet.app", hidden:false}'
osascript -e 'tell application "System Events" to make login item at end with properties {path:"/Applications/Handy.app", hidden:false}'
```

Открыть вручную: `open -a Comet` и `open -a Handy`.

TTS поднимется сам при следующей озвучке.

## Результат (28.11, 04:46)

- Login items: только Google Drive. Comet и Handy убраны.
- Comet не был запущен — удалён из автозапуска; Handy закрыт; TTS-сервер остановлен.
- Память: было 15 ГБ занято и ~0,7 ГБ свободно; стало 13 ГБ занято и ~2,3–2,4 ГБ свободно. Своп 0.
- Chrome 9224 жив, одна вкладка.
- Chrome после перезагрузки сам не стартует — для Flowwow нужен отдельный автозапуск.

## Поправка 04:58

Владелец работает с Handy постоянно. Вернул `autostart_enabled=true` из бэкапа, login item Handy и запустил приложение. **Handy не отключать.**
