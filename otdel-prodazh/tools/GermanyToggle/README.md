# GermanyToggle — переключатель в строке меню

Приложение для macOS: один клик в строке меню включает/выключает немецкий прокси для приложений (ChatGPT, Claude и др.).

## Что делает

| Состояние | Что происходит |
|---|---|
| **🇩🇪 ВКЛ** | системный прокси `127.0.0.1:8118` включён → приложения ходят через Германию |
| **🇩🇪 выкл** | прокси выключен → российский IP (нужно для Авито) |

Мой канал (связь с моделью) не затрагивается: терминалы системный прокси не используют.

## Установка

```bash
swiftc -O main.swift -o GermanyToggle -framework Cocoa
mkdir -p GermanyToggle.app/Contents/MacOS
cp GermanyToggle GermanyToggle.app/Contents/MacOS/
# Info.plist: LSUIElement=true, bundle id ru.silversong.germany
cp -R GermanyToggle.app /Applications/
open -a /Applications/GermanyToggle.app
```

Добавлено в автозапуск (Login Items) — появляется при входе в систему.

## Зависимость

Локальный прокси `otdel-prodazh/tools/local-proxy.py` — приложение поднимает его само, если не запущен.
