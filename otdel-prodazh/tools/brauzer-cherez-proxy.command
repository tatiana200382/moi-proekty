#!/bin/bash
# Chrome через Германию: локальный прокси 127.0.0.1:8118 (без пароля) → немецкий сервер.
# Запуск: дважды щёлкнуть файл. Аргумент — адрес сайта.
PY="/Applications/DeepSeek Harness.app/Contents/Resources/runtime/primary-runtime/dependencies/python/bin/python3"
ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
PROFILE="$HOME/.chrome-proxy-germany"
URL="${1:-https://chatgpt.com}"

# поднять локальный прокси, если не отвечает
if ! curl -s -m 2 -x http://127.0.0.1:8118 https://api.ipify.org >/dev/null 2>&1; then
  nohup "$PY" "$ROOT/otdel-prodazh/tools/local-proxy.py" >/tmp/local-proxy.log 2>&1 &
  sleep 2
fi

open -na "Google Chrome" --args \
  --proxy-server="http://127.0.0.1:8118" \
  --user-data-dir="$PROFILE" \
  --no-first-run --lang=ru "$URL"
