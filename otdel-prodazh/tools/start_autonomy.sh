#!/bin/bash
# Запускает автономный цикл в фоне (без окна Терминала).
set -u
ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
cd "$ROOT" || exit 1
PIDFILE="$ROOT/otdel-prodazh/runtime/watch.pid"
LOG="$ROOT/otdel-prodazh/runtime/logs/watch.log"
mkdir -p "$ROOT/otdel-prodazh/runtime/logs"

if [ -f "$PIDFILE" ]; then
  OLD="$(cat "$PIDFILE" 2>/dev/null)"
  if [ -n "$OLD" ] && kill -0 "$OLD" 2>/dev/null && ps -p "$OLD" -o command= 2>/dev/null | grep -q "watch-sales.command"; then
    echo "Уже работает (PID $OLD)"
    exit 0
  fi
fi

nohup "$ROOT/otdel-prodazh/tools/watch-sales.command" >> "$LOG" 2>&1 &
sleep 2
if [ -f "$PIDFILE" ] && kill -0 "$(cat "$PIDFILE" 2>/dev/null)" 2>/dev/null; then
  echo "Запущено в фоне (PID $(cat "$PIDFILE")). Лог: $LOG"
else
  echo "Не запустилось — смотри $LOG"
  exit 1
fi
