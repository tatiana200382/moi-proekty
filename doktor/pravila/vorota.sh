#!/bin/bash
# Ворота Доктора: не пускают рискованное действие без условий владельца.
# Проверяет план, «да», откат, изолированный тест, стоп-флаг и лимиты площадки.
#
# Использование:
#   vorota.sh --tip server      --plan plany/2026-11-25-x.md
#   vorota.sh --tip dengi       --plan plany/2026-11-25-x.md
#   vorota.sh --tip chuzhoe     --plan plany/2026-11-25-x.md
#   vorota.sh --tip publikaciya --ploshchadka avito --odobreno
#   vorota.sh --tip pravka      --ploshchadka avito --odobreno
#
# Код выхода: 0 — можно, 1 — нельзя (причина в выводе), 2 — ошибка вызова.

set -uo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
DIR="$ROOT/doktor/pravila"
STOP="$DIR/STOP"
LOG="$DIR/resheniya.md"
COUNTERS="$DIR/schetchiki"
MAX_PUB_DAY=3
EDIT_COOLDOWN_SEC=3600

TIP=""; PLAN=""; PLOSHCHADKA=""; ODOBRENO=0
while [ $# -gt 0 ]; do
  case "$1" in
    --tip) TIP="${2:-}"; shift 2 ;;
    --plan) PLAN="${2:-}"; shift 2 ;;
    --ploshchadka) PLOSHCHADKA="${2:-}"; shift 2 ;;
    --odobreno) ODOBRENO=1; shift ;;
    *) echo "неизвестный аргумент: $1"; exit 2 ;;
  esac
done
[ -n "$TIP" ] || { echo "нужен --tip"; exit 2; }
mkdir -p "$COUNTERS"

deny() {
  local reason="$1"
  printf '%s ОТКАЗ  %-10s %-30s %s\n' "$(date '+%Y-%m-%d %H:%M')" "$TIP" "${PLAN:-$PLOSHCHADKA}" "$reason"
  echo "| $(date '+%Y-%m-%d %H:%M') | $TIP | ${PLAN:-$PLOSHCHADKA} | ОТКАЗ: $reason |" >> "$LOG"
  exit 1
}
allow() {
  local note="$1"
  printf '%s ДОПУСК %-10s %-30s %s\n' "$(date '+%Y-%m-%d %H:%M')" "$TIP" "${PLAN:-$PLOSHCHADKA}" "$note"
  echo "| $(date '+%Y-%m-%d %H:%M') | $TIP | ${PLAN:-$PLOSHCHADKA} | ДОПУСК: $note |" >> "$LOG"
  exit 0
}

# 0. Стоп-флаг — общий для всех.
[ -f "$STOP" ] && deny "включён STOP (решение владельца или 3 нарушения)"

need_plan() {
  local p="$ROOT/$1"
  [ -f "$p" ] || deny "нет плана: $1"
  grep -q "Разрешение владельца" "$p" || deny "в плане нет строки о разрешении владельца"
  grep -qE "получено|разрешено" "$p" || deny "разрешение владельца не отмечено как полученное"
  grep -q "Откат" "$p" || deny "в плане нет раздела «Откат»"
  grep -qiE "изолирован|тестов" "$p" || deny "в плане нет проверки на изолированном участке"
}

case "$TIP" in
  server|dengi|chuzhoe)
    [ -n "$PLAN" ] || deny "для этого типа нужен --plan"
    need_plan "$PLAN"
    allow "план полный, разрешение есть"
    ;;
  publikaciya)
    [ -n "$PLOSHCHADKA" ] || deny "нужен --ploshchadka"
    [ "$ODOBRENO" -eq 1 ] || deny "нет отметки «одобрено владельцем» (--odobreno)"
    today="$(date '+%Y-%m-%d')"
    f="$COUNTERS/${PLOSHCHADKA}-${today}.cnt"
    n=$(cat "$f" 2>/dev/null || echo 0)
    [ "$n" -lt "$MAX_PUB_DAY" ] || deny "лимит: $MAX_PUB_DAY публикации в день для $PLOSHCHADKA"
    echo $((n + 1)) > "$f"
    allow "публикация $((n + 1))/$MAX_PUB_DAY за $today"
    ;;
  pravka)
    [ -n "$PLOSHCHADKA" ] || deny "нужен --ploshchadka"
    [ "$ODOBRENO" -eq 1 ] || deny "правка без согласования (--odobreno)"
    last="$COUNTERS/${PLOSHCHADKA}-last-edit"
    now=$(date +%s)
    if [ -f "$last" ]; then
      prev=$(cat "$last")
      delta=$((now - prev))
      [ "$delta" -ge "$EDIT_COOLDOWN_SEC" ] || deny "правка была $((delta / 60)) мин назад — нужно 60"
    fi
    echo "$now" > "$last"
    allow "правка разрешена (прошло больше часа)"
    ;;
  *) echo "неизвестный --tip: $TIP"; exit 2 ;;
esac
