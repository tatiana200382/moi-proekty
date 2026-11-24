#!/bin/bash
# Резервный режим на Mac: включается только если сервер молчит.
# Проверяет /health на сервере; если 3 раза подряд нет ответа — запускает опрос и пишет в MAX.
set -uo pipefail
ROOT="/Users/tatiana/Desktop/Обучение ИИ/proekty/Мои проекты"
SERVER="${SERVER_HEALTH_URL:-http://ai.m-tik.com:8790/health}"
STATE="/tmp/asar/standby-fails"
LOG="/tmp/asar/standby.log"
mkdir -p /tmp/asar
fails=$(cat "$STATE" 2>/dev/null || echo 0)

if curl -sS -m 6 "$SERVER" 2>/dev/null | grep -q '"ok": true'; then
  echo "$(date '+%F %T') сервер жив — резерв не нужен" >> "$LOG"
  echo 0 > "$STATE"
  exit 0
fi

fails=$((fails + 1)); echo "$fails" > "$STATE"
echo "$(date '+%F %T') сервер не ответил ($fails/3)" >> "$LOG"

if [ "$fails" -ge 3 ]; then
  echo "$(date '+%F %T') включаю резерв на Mac" >> "$LOG"
  cd "$ROOT" && bash otdel-prodazh/run.sh >> "$LOG" 2>&1
  PY="/Applications/DeepSeek Harness.app/Contents/Resources/runtime/primary-runtime/dependencies/python/bin/python3"
  "$PY" -c "
import sys; sys.path.insert(0,'agent-marketolog/bot')
import max_client
max_client.send(max_client.chat_id(), '⚠️ Сервер не отвечает — включился резерв на Mac. Проверьте сервер.')
" >> "$LOG" 2>&1
fi
