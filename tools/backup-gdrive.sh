#!/bin/bash
# Резервная копия хранилища Obsidian и папки секретаря в Google Диск.
# Запуск: ./tools/backup-gdrive.sh   (или по расписанию, launchd)
set -uo pipefail

VAULT="$HOME/Desktop/Обучение ИИ/vault/AI-Memory-Lab"
SECRETARY="$HOME/Desktop/Обучение ИИ/Секретарь"
GD="$HOME/Library/CloudStorage/GoogleDrive-tatiana200382@gmail.com/Мой диск/Резервные копии ИИ"
IF_OLD=0
[ "${1:-}" = "--if-old" ] && IF_OLD="${2:-20}"
STAMP="$(date '+%Y-%m-%d_%H-%M')"
LOG="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/backup.log"

say() { printf '%s %s\n' "$(date '+%Y-%m-%d %H:%M')" "$*" | tee -a "$LOG"; }

[ -d "$GD" ] || { mkdir -p "$GD" 2>/dev/null; }
[ -d "$GD" ] || { say "ОШИБКА: нет доступа к Google Диску: $GD"; exit 1; }

# Не делать копию чаще, чем раз в IF_OLD часов.
if [ "$IF_OLD" -gt 0 ] && [ -d "$GD" ]; then
  NEWEST="$(ls -1d "$GD"/*/ 2>/dev/null | sort | tail -1)"
  if [ -n "$NEWEST" ]; then
    AGE_H=$(( ( $(date +%s) - $(stat -f %m "$NEWEST") ) / 3600 ))
    if [ "$AGE_H" -lt "$IF_OLD" ]; then
      echo "копия свежая ($AGE_H ч), пропускаю"
      exit 0
    fi
  fi
fi

STAGE="$GD/$STAMP"
mkdir -p "$STAGE" || { say "ОШИБКА: не удалось создать $STAGE"; exit 1; }

rc=0
if [ -d "$VAULT" ]; then
  if ditto -c -k --sequesterRsrc --keepParent "$VAULT" "$STAGE/AI-Memory-Lab-$STAMP.zip" 2>>"$LOG"; then
    say "хранилище: $(du -h "$STAGE/AI-Memory-Lab-$STAMP.zip" | cut -f1)"
  else
    say "ОШИБКА: архив хранилища не создан"; rc=1
  fi
else
  say "ПРЕДУПРЕЖДЕНИЕ: нет папки хранилища $VAULT"; rc=1
fi

if [ -d "$SECRETARY" ]; then
  if ditto -c -k --sequesterRsrc --keepParent "$SECRETARY" "$STAGE/Секретарь-$STAMP.zip" 2>>"$LOG"; then
    say "секретарь: $(du -h "$STAGE/Секретарь-$STAMP.zip" | cut -f1)"
  else
    say "ОШИБКА: архив секретаря не создан"; rc=1
  fi
else
  say "ПРЕДУПРЕЖДЕНИЕ: нет папки секретаря $SECRETARY"; rc=1
fi

# Оставляем 10 последних копий.
LIST="$(mktemp)"
ls -1d "$GD"/*/ 2>/dev/null | sort > "$LIST"
N=$(wc -l < "$LIST" | tr -d ' ')
if [ "${N:-0}" -gt 10 ]; then
  head -n "$((N - 10))" "$LIST" | while IFS= read -r old; do
    rm -rf "$old" && say "удалена старая копия: $(basename "$old")"
  done
fi
rm -f "$LIST"

say "готово: $STAGE"
exit $rc
