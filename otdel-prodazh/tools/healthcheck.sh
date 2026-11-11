#!/bin/bash
# Проверка здоровья автономного отдела продаж.
set -u
ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
cd "$ROOT" || exit 1
ok=0; bad=0
say_ok() { echo "OK   $1"; ok=$((ok+1)); }
say_bad() { echo "НЕТ  $1"; bad=$((bad+1)); }

if curl -s --max-time 4 http://127.0.0.1:9224/json/version | grep -q Browser; then
  say_ok "Chrome CDP 9224"
else
  say_bad "Chrome CDP 9224 — запустить run.sh или открыть Chrome с профилем"
fi

if python3 agent-marketolog/bot/max_client.py me 2>/dev/null | grep -q '"is_bot": true'; then
  say_ok "MAX-бот отвечает"
else
  say_bad "MAX-бот — проверить токен ~/.config/max-bot/token"
fi

PIDFILE="$ROOT/otdel-prodazh/runtime/watch.pid"
if [ -f "$PIDFILE" ] && kill -0 "$(cat "$PIDFILE" 2>/dev/null)" 2>/dev/null; then
  say_ok "автономный цикл работает (PID $(cat "$PIDFILE"))"
else
  say_bad "автономный цикл не запущен — tools/start_autonomy.sh"
fi

if osascript -e 'tell application "System Events" to get the name of every login item' 2>/dev/null | grep -q "watch-sales.command"; then
  say_ok "автозагрузка при входе"
else
  say_bad "автозагрузка при входе — добавить watch-sales.command в Login Items"
fi

echo "---"
python3 otdel-prodazh/tools/sales_pipeline.py --status
echo "---"
echo "Всего OK: $ok, проблем: $bad"
