#!/bin/bash
# Один цикл автономного отдела продаж.
# Запускается launchd каждые 5 минут. Вручную — для проверки.
set -u

ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
cd "$ROOT" || exit 1

export PATH="/usr/local/bin:/opt/homebrew/bin:/usr/bin:/bin:/usr/sbin:/sbin"
export PYTHONDONTWRITEBYTECODE=1

LOG="$ROOT/otdel-prodazh/runtime/logs/run.log"
mkdir -p "$ROOT/otdel-prodazh/runtime/logs"

# Ротация: не даём логу расти бесконечно.
if [ -f "$LOG" ] && [ "$(stat -f%z "$LOG" 2>/dev/null || echo 0)" -gt 5000000 ]; then
  mv "$LOG" "$LOG.1"
fi

echo "=== $(date '+%Y-%m-%d %H:%M:%S') ===" >> "$LOG"

# 1. Chrome с отладкой. Без него не читаются кабинеты.
if ! curl -s --max-time 4 http://127.0.0.1:9224/json/version | grep -q Browser; then
  echo "Chrome CDP не отвечает — пробую запустить" >> "$LOG"
  CHROME="/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
  if [ -x "$CHROME" ]; then
    "$CHROME" --remote-debugging-port=9224 \
      --user-data-dir="$ROOT/.chrome-profile" \
      --lang=ru --no-first-run >/dev/null 2>&1 &
    sleep 12
  else
    echo "Chrome не найден: $CHROME" >> "$LOG"
  fi
fi

# 2. Сбор заявок с площадок. Без --send: карточки шлёт отдел продаж, а не бот.
python3 agent-marketolog/bot/collect.py all >> "$LOG" 2>&1
COLLECT=$?
echo "collect exit=$COLLECT" >> "$LOG"

# 3. Продажи: новые заявки → готовые карточки → MAX → итоги по расписанию.
python3 otdel-prodazh/tools/sales_pipeline.py --auto >> "$LOG" 2>&1
echo "pipeline exit=$?" >> "$LOG"
