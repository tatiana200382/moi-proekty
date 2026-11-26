# Codex внутри ChatGPT.app: прокси через локальный HTTP-прокси

Дата: 25.11.2026. Разрешение владельца: **получено**.

## Проблема
Вход в **Codex** не проходил: `token_exchange_failed`, `403 Country, region, or territory not supported`.
Причина: `codex-cli` — отдельный процесс (Rust), не читает системный SOCKS-прокси macOS; запросы уходили напрямую с российского адреса.

## Что сработало
Локальный **HTTP-прокси** `127.0.0.1:8118`, который пересылает трафик через наш SOCKS-туннель (`127.0.0.1:1082` → наш сервер `2.31.104.44`), плюс переменные окружения для GUI-приложений.

```
launchctl setenv HTTPS_PROXY http://127.0.0.1:8118
launchctl setenv HTTP_PROXY  http://127.0.0.1:8118
launchctl setenv ALL_PROXY   http://127.0.0.1:8118
```

Проверено владельцем: **вход в Codex прошёл**.

## Что установлено
| Компонент | Где |
|---|---|
| HTTP-прокси | `~/Library/Application Support/silversong/http-via-socks.py` |
| Автозапуск прокси | LaunchAgent `ru.silversong.httpproxy` (KeepAlive) |
| Переменные окружения | `launchctl setenv` (для приложений, запущенных после) |

## Откат (если понадобится)
```
launchctl unsetenv HTTPS_PROXY; launchctl unsetenv HTTP_PROXY; launchctl unsetenv ALL_PROXY
launchctl unload ~/Library/LaunchAgents/ru.silversong.httpproxy.plist
```
Затем перезапустить ChatGPT.app.

## Важно
- Переменные действуют на приложения, запущенные **после** установки.
- Системный SOCKS-прокси и SSH-туннель остаются как были.
- После перезагрузки Mac: LaunchAgent поднимет прокси, переменные `launchctl setenv` **не сохраняются** — их нужно задать заново (добавлено в задачи).

## Автозапуск после перезагрузки (добавлено)

| Что | Как |
|---|---|
| HTTP-прокси | LaunchAgent `ru.silversong.httpproxy` (KeepAlive) |
| Переменные окружения | LaunchAgent `ru.silversong.proxyenv` (RunAtLoad, скрипт `set-proxy-env.sh`) |
| SOCKS-туннель | LaunchAgent `ru.silversong.socks` |
| Сторож | LaunchAgent `ru.silversong.watchdog` |

## Проверка после настройки автозапуска
| Проверка | Результат |
|---|---|
| Переменные после перезагрузки агента | ✅ задались автоматически |
| SSH-туннель | ✅ `2.31.104.44` |
| HTTP-прокси | ✅ `2.31.104.44` |
| Системный SOCKS | ✅ включён |
| Исключения (Авито, ВК) | ✅ на месте |
| OpenAI через HTTP-прокси | ✅ 401 |
| chatgpt.com через туннель | ✅ 200 |

**Итог: после перезагрузки Мака ничего вручную задавать не нужно.**
