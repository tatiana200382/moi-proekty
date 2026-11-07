#!/bin/bash
# Голос ассистента: локальный Silero-сервер → Piper → say Milena.
# Использование: ./skazat.sh "текст" [скорость]
set -uo pipefail
[ $# -ge 1 ] || { echo 'usage: ./skazat.sh "текст" [скорость]' >&2; exit 1; }
TEXT="$1"; RATE="${2:-180}"
DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PORT=8765
OUT="$(mktemp -t skazat).wav"

ready() { curl -s -m 1 -o /dev/null "http://127.0.0.1:$PORT/say?text=" ; }

# Поднять сервер, если не запущен.
if ! ready; then
  nohup "$HOME/.tts-venv/bin/python" "$DIR/tools/tts_server.py" >/tmp/tts_server.log 2>&1 &
  for _ in $(seq 1 40); do sleep 0.5; ready && break; done
fi

# 1) Silero через сервер.
if ready; then
  if curl -s -m 60 -G --data-urlencode "text=$TEXT" --data-urlencode "speaker=baya" "http://127.0.0.1:$PORT/say" -o "$OUT" && [ -s "$OUT" ]; then
    afplay -v 2.0 "$OUT"; rm -f "$OUT"; exit 0
  fi
fi

# 2) Piper.
if [ -x "$HOME/.tts-venv/bin/piper" ] && [ -f "$HOME/.tts-voices/ru_RU-irina-medium.onnx" ]; then
  if printf '%s\n' "$TEXT" | "$HOME/.tts-venv/bin/piper" -m "$HOME/.tts-voices/ru_RU-irina-medium.onnx" -f "$OUT" >/dev/null 2>&1 && [ -s "$OUT" ]; then
    afplay -v 2.2 "$OUT"; rm -f "$OUT"; exit 0
  fi
fi

# 3) Системный голос.
rm -f "$OUT"; say -v Milena -r "$RATE" -- "$TEXT"
