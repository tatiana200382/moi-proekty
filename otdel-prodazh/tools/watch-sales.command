#!/bin/bash
# Автономный отдел продаж: цикл каждые 5 минут.
# Можно запускать двойным щелчком или из автозагрузки.
# Окно Терминала можно свернуть, но не закрывать.
set -u

ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
cd "$ROOT" || exit 1

PIDFILE="$ROOT/otdel-prodazh/runtime/watch.pid"
LOG="$ROOT/otdel-prodazh/runtime/logs/watch.log"
mkdir -p "$ROOT/otdel-prodazh/runtime/logs"

if [ -f "$PIDFILE" ]; then
  OLD="$(cat "$PIDFILE" 2>/dev/null)"
  if [ -n "$OLD" ] && kill -0 "$OLD" 2>/dev/null && ps -p "$OLD" -o command= 2>/dev/null | grep -q "watch-sales.command"; then
    echo "Отдел продаж уже работает (PID $OLD)"
    exit 0
  fi
fi

echo $$ > "$PIDFILE"
trap 'rm -f "$PIDFILE"' EXIT

echo "=== старт $(date '+%Y-%m-%d %H:%M:%S') ===" >> "$LOG"
while true; do
  "$ROOT/otdel-prodazh/tools/run.sh" >> "$LOG" 2>&1
  sleep 300
done
