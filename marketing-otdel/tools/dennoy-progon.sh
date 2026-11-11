#!/bin/bash
# dennoy-progon.sh — ежедневный прогон отдела: доступы → данные → отчёт → дашборд.
# Сырые дампы кабинетов хранятся ВНЕ репозитория (там персональные данные).
set -uo pipefail

DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
DATE="$(date +%F)"
DUMPS="$HOME/.local/state/marketing/$DATE"
mkdir -p "$DUMPS" "$DIR/results"

say() { printf '%s\n' "$*"; }

if ! curl -s -m 2 http://127.0.0.1:9224/json/version >/dev/null; then
  say "✗ Chrome под управлением не запущен (порт 9224)."
  say "  Запусти: open -na 'Google Chrome' --args --remote-debugging-port=9224 --user-data-dir=\"$DIR/../.chrome-profile\""
  exit 1
fi

say "1/4 Проверяю входы…"
node "$DIR/tools/browser.mjs" login-status | tee "$DUMPS/logins.txt"

say "2/4 Снимаю Яндекс.Бизнес…"
node "$DIR/tools/browser.mjs" text "https://yandex.ru/business/statistic/company/138890152139" --wait 8000 --out "$DUMPS/yandex.txt"

say "3/4 Снимаю Авито…"
node "$DIR/tools/browser.mjs" text "https://www.avito.ru/profile/items" --wait 8000 --out "$DUMPS/avito.txt"

say "4/4 Собираю отчёт и дашборд…"
python3 "$DIR/tools/report.py" --out "$DIR/results/otchet-$DATE.md"
python3 "$DIR/tools/dashboard.py" --out "$DIR/results/dashboard.html"

say "Готово."
say "  отчёт:     $DIR/results/otchet-$DATE.md"
say "  дашборд:   $DIR/results/dashboard.html"
say "  сырые данные: $DUMPS (вне git)"
