#!/bin/bash
# Опрос площадок и отправка новых заявок в MAX.
# Двойной щелчок в Finder запускает цикл; окно Терминала должно быть открыто.
# Остановить — закрыть окно Терминала или нажать Ctrl+C.
cd "$(dirname "$0")/.." || exit 1
export PYTHONDONTWRITEBYTECODE=1
while true; do
  echo "=== $(date '+%Y-%m-%d %H:%M:%S') ==="
  python3 bot/collect.py all --send
  sleep 300
done
