#!/bin/bash
# Сторож человекоподобного режима Авито.
#   avito-guard.sh check   -> 0 (можно) / 1 (рано) — печатает причину
#   avito-guard.sh done ok|limit|block  -> планирует следующий запуск
set -u
ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
RT="$ROOT/otdel-prodazh/runtime"
NEXT="$RT/avito-next-run.ts"
BLOCK="$RT/avito-blocked-until.ts"
mkdir -p "$RT"

now=$(date +%s)

case "${1:-check}" in
  check)
    if [ -f "$BLOCK" ]; then
      until=$(cat "$BLOCK" 2>/dev/null || echo 0)
      if [ "$now" -lt "$until" ]; then
        echo "Авито: пауза после проверки IP, ещё $(( (until-now)/60 )) мин"
        exit 1
      fi
    fi
    if [ -f "$NEXT" ]; then
      next=$(cat "$NEXT" 2>/dev/null || echo 0)
      if [ "$now" -lt "$next" ]; then
        echo "Авито: рано, ещё $(( (next-now)/60 )) мин (человеческий интервал)"
        exit 1
      fi
    fi
    exit 0
    ;;
  done)
    status="${2:-ok}"
    case "$status" in
      ok)     pause=$(( 900 + RANDOM % 300 )) ;;   # 15–20 мин
      limit)  pause=$(( 3600 + RANDOM % 1200 )) ;; # 60–80 мин после 429
      block)  pause=$(( 5400 + RANDOM % 1800 )) ;; # 90–120 мин после «проверки IP»
      *)      pause=900 ;;
    esac
    echo $(( now + pause )) > "$NEXT"
    if [ "$status" = "block" ]; then
      echo $(( now + 5400 )) > "$BLOCK"
    fi
    echo "Авито: следующий заход через $(( pause/60 )) мин (статус $status)"
    exit 0
    ;;
  *) echo "usage: avito-guard.sh check|done ok|limit|block"; exit 2 ;;
esac
