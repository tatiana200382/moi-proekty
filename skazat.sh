#!/bin/bash
# Голос ассистента. По умолчанию — нейросетевой Piper (ru_RU-irina), запасной — say Milena.
# Использование: ./skazat.sh "текст" [скорость]
set -euo pipefail
[ $# -ge 1 ] || { echo 'usage: ./skazat.sh "текст" [скорость]' >&2; exit 1; }
TEXT="$1"
RATE="${2:-180}"

PIPER="$HOME/.tts-venv/bin/piper"
VOICE="$HOME/.tts-voices/ru_RU-irina-medium.onnx"
OUT="$(mktemp -t skazat).wav"

if [ -x "$PIPER" ] && [ -f "$VOICE" ]; then
  if printf '%s\n' "$TEXT" | "$PIPER" -m "$VOICE" -f "$OUT" --length_scale 1.0 >/dev/null 2>&1; then
    afplay -v 2.2 "$OUT" || true
    rm -f "$OUT"
    exit 0
  fi
fi

rm -f "$OUT"
say -v Milena -r "$RATE" -- "$TEXT"
