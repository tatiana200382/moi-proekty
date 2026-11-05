#!/bin/bash
# Голос Котика: озвучивает текст голосом Milena (ru_RU).
# Использование: ./skazat.sh "текст" [скорость]
set -euo pipefail
[ $# -ge 1 ] || { echo 'usage: ./skazat.sh "текст" [скорость]' >&2; exit 1; }
RATE="${2:-180}"
say -v Milena -r "$RATE" -- "$1"
