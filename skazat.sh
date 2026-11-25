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

# 1) Silero через сервер (длинный текст режем на куски — модель не берёт длинные).
if ready; then
  OK=1
  while IFS= read -r CHUNK; do
    [ -z "$CHUNK" ] && continue
    if curl -s -m 90 -G --data-urlencode "text=$CHUNK" --data-urlencode "speaker=baya" "http://127.0.0.1:$PORT/say" -o "$OUT" \
       && [ -s "$OUT" ] && [ "$(head -c 4 "$OUT" 2>/dev/null)" = "RIFF" ]; then
      afplay -v 2.0 "$OUT" || OK=0
    else
      OK=0; break
    fi
  done < <("$HOME/.tts-venv/bin/python" - "$TEXT" <<'PYCH'
import sys, re
t = sys.argv[1]
parts = re.split(r'(?<=[.!?…])\s+', t)
buf = ""
for p in parts:
    if len(buf) + len(p) > 180 and buf:
        print(buf); buf = p
    else:
        buf = (buf + " " + p).strip()
if buf:
    print(buf)
PYCH
)
  rm -f "$OUT"
  [ "$OK" = "1" ] && exit 0
fi

# 2) Piper.
if [ -x "$HOME/.tts-venv/bin/piper" ] && [ -f "$HOME/.tts-voices/ru_RU-irina-medium.onnx" ]; then
  if printf '%s\n' "$TEXT" | "$HOME/.tts-venv/bin/piper" -m "$HOME/.tts-voices/ru_RU-irina-medium.onnx" -f "$OUT" >/dev/null 2>&1 && [ -s "$OUT" ]; then
    afplay -v 2.2 "$OUT"; rm -f "$OUT"; exit 0
  fi
fi

# 3) Системный голос.
rm -f "$OUT"; say -v Milena -r "$RATE" -- "$TEXT"
