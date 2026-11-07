#!/bin/bash
# Рендер HTML в PNG через Chrome headless. Установка не нужна.
# Использование: ./tools/render.sh templates/post-card.html results/out.png 1080 1350
set -euo pipefail
CHROME="/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
IN="$1"; OUT="$2"; W="${3:-1080}"; H="${4:-1350}"
[ -f "$IN" ] || { echo "нет файла $IN" >&2; exit 1; }
ABS_IN="$(cd "$(dirname "$IN")" && pwd)/$(basename "$IN")"
mkdir -p "$(dirname "$OUT")"
ABS_OUT="$(cd "$(dirname "$OUT")" && pwd)/$(basename "$OUT")"
"$CHROME" --headless=new --no-sandbox --disable-gpu --disable-dev-shm-usage --hide-scrollbars \
  --user-data-dir=/tmp/chrome-render-profile \
  --window-size="${W},${H}" --screenshot="$ABS_OUT" \
  "file://$ABS_IN" >/dev/null 2>&1
[ -f "$ABS_OUT" ] && echo "готово: $ABS_OUT"
