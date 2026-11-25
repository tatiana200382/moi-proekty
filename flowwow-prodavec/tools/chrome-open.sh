#!/bin/bash
# Запуск управляемого Chrome для Flowwow — видимым окном, порт 9224.
# Headless использовать нельзя: Flowwow отдаёт «Forbidden» (проверено 25.11.2026).
# Проверка после запуска: curl -s http://127.0.0.1:9224/json/version | grep User-Agent

set -euo pipefail

PORT=9224
PROFILE="/Users/tatiana/Desktop/Обучение ИИ/proekty/Мои проекты/.chrome-profile"
CHROME="/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"

if curl -s -m 2 "http://127.0.0.1:${PORT}/json/version" >/dev/null; then
  echo "порт ${PORT} уже занят — Chrome запущен"
  curl -s "http://127.0.0.1:${PORT}/json/version" | grep -m1 User-Agent
  exit 0
fi

nohup "$CHROME" \
  --remote-debugging-port="$PORT" \
  --user-data-dir="$PROFILE" \
  --lang=ru --no-first-run --noerrdialogs \
  >/tmp/ff-chrome.log 2>&1 &

sleep 6
UA=$(curl -s -m 3 "http://127.0.0.1:${PORT}/json/version" | grep -m1 User-Agent || true)
if [ -z "$UA" ]; then
  echo "Chrome не поднялся, лог: /tmp/ff-chrome.log"
  exit 1
fi
echo "$UA"
case "$UA" in
  *HeadlessChrome*) echo "ВНИМАНИЕ: браузер в headless — Flowwow заблокирует" ;;
  *) echo "ок: видимое окно, порт ${PORT}" ;;
esac
