#!/bin/bash
# Включает системный прокси: приложения (ChatGPT, Claude) ходят через Германию.
# Мой канал не затрагивается — терминалы прокси не используют.
PY="/Applications/DeepSeek Harness.app/Contents/Resources/runtime/primary-runtime/dependencies/python/bin/python3"
ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
SERV="Wi-Fi"   # сеть, через которую работает Mac

if ! curl -s -m 2 -x http://127.0.0.1:8118 https://api.ipify.org >/dev/null 2>&1; then
  nohup "$PY" "$ROOT/otdel-prodazh/tools/local-proxy.py" >/tmp/local-proxy.log 2>&1 &
  sleep 2
fi

networksetup -setwebproxy "$SERV" 127.0.0.1 8118
networksetup -setsecurewebproxy "$SERV" 127.0.0.1 8118
echo "прокси включён для сети «$SERV»"
networksetup -getwebproxy "$SERV" | head -3
