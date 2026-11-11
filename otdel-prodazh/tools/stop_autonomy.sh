#!/bin/bash
# Останавливает автономный цикл.
set -u
ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
PIDFILE="$ROOT/otdel-prodazh/runtime/watch.pid"
if [ -f "$PIDFILE" ]; then
  PID="$(cat "$PIDFILE" 2>/dev/null)"
  if kill -0 "$PID" 2>/dev/null; then
    kill "$PID" 2>/dev/null || true
    echo "Остановлено (PID $PID)"
  else
    echo "Процесс уже не работает"
  fi
  rm -f "$PIDFILE"
else
  echo "Автономный цикл не запущен"
fi
