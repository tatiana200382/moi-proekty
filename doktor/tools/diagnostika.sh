#!/bin/bash
# Диагностика рабочей области «Мои проекты». Только читает, ничего не меняет.
# Использование: doktor/tools/diagnostika.sh [--verbose]
# Код выхода: 0 — всё в порядке, 1 — есть поломки (FAIL).

set -uo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$ROOT" || exit 2

OK=0; WARN=0; FAIL=0; NOTES=""
ok()   { OK=$((OK+1));   printf 'OK    %s\n' "$1"; }
warn() { WARN=$((WARN+1)); printf 'WARN  %s\n' "$1"; NOTES="$NOTES$1\n"; }
fail() { FAIL=$((FAIL+1)); printf 'FAIL  %s\n' "$1"; NOTES="$NOTES$1\n"; }

echo "== Доктор: диагностика =="
echo "Корень: $ROOT"
echo

echo "-- 1. Ключевые файлы --"
for f in PRAVILA.md AGENTS.md CLAUDE.md STRUKTURA.md komanda.md shablon-agenta.md \
         uroki.md skazat.sh profil-ai.md plan-testov.md doktor/AGENTS.md; do
  if [ -e "$f" ]; then ok "файл: $f"; else fail "нет файла: $f"; fi
done
echo

echo "-- 2. Симлинки (obsidian, sekretar, профили Chrome) --"
for l in obsidian sekretar .chrome-profile .browser-profile .chrome-maps; do
  if [ ! -L "$l" ]; then
    warn "нет симлинка: $l"
  elif [ -e "$l" ]; then
    ok "ссылка живёт: $l → $(readlink "$l")"
  else
    fail "битый симлинк: $l → $(readlink "$l")"
  fi
done
echo

echo "-- 3. Ссылки на файлы в ключевых документах --"
link_errors=0
for doc in PRAVILA.md AGENTS.md CLAUDE.md STRUKTURA.md komanda.md doktor/AGENTS.md; do
  [ -f "$doc" ] || continue
  dir="$(dirname "$doc")"
  while IFS= read -r target; do
    case "$target" in
      http*|https*|mailto:*|"#"*) continue ;;
    esac
    target="${target%%#*}"
    [ -e "$dir/$target" ] || { fail "битая ссылка: $doc → $target"; link_errors=$((link_errors+1)); }
  done < <(grep -oE '\]\([^)]+\)' "$doc" 2>/dev/null | sed 's/^](//; s/)$//')
done
[ "$link_errors" -eq 0 ] && ok "битых ссылок нет"
echo

echo "-- 4. Скрипты --"
for s in skazat.sh doktor/tools/diagnostika.sh; do
  if [ -f "$s" ] && [ -x "$s" ]; then ok "исполняемый: $s"
  elif [ -f "$s" ]; then warn "нет права на запуск: $s"
  else fail "нет скрипта: $s"; fi
done
if [ -f "ii-marketolog/tools/cdp.mjs" ]; then ok "cdp.mjs на месте (запуск через node)"
else warn "нет ii-marketolog/tools/cdp.mjs — браузерные задачи не заработают"; fi
echo

echo "-- 5. Git --"
if git rev-parse --git-dir >/dev/null 2>&1; then
  branch="$(git branch --show-current 2>/dev/null)"
  ok "репозиторий, ветка: ${branch:-detached}"
  dirty="$(git status --porcelain 2>/dev/null | wc -l | tr -d ' ')"
  if [ "$dirty" -eq 0 ]; then ok "рабочее дерево чистое"
  else warn "незакоммиченных изменений: $dirty"; fi
  # Секреты — это обычные файлы в профиле. Симлинк на ~/.config безопасен.
  leaked="$(git ls-files -s 2>/dev/null | grep -E '(chrome-profile|browser-profile)/?' | awk '$1 ~ /^100/ {c++} END {print c+0}')"
  if [ "${leaked:-0}" -eq 0 ]; then ok "содержимое профилей браузера не в git (симлинки — ок)"
  else fail "в git попали файлы профиля браузера: $leaked"; fi
else
  fail "это не git-репозиторий"
fi
echo

echo "-- 6. Chrome (CDP 9224) --"
if curl -s -m 2 http://127.0.0.1:9224/json/version >/dev/null 2>&1; then
  ok "Chrome отвечает на 9224"
else
  warn "Chrome на 9224 не отвечает (нужен только для работы с сайтами)"
fi
echo

echo "-- 7. Голос (TTS 8765) --"
if curl -s -m 1 http://127.0.0.1:8765/say?text= >/dev/null 2>&1; then
  ok "TTS-сервер 8765 работает"
else
  warn "TTS-сервер 8765 не поднят (skazat.sh поднимет сам)"
fi
echo

echo "-- 8. Obsidian --"
VAULT="$HOME/AI-Memory-Lab"
if [ -d "$VAULT/01_проекты" ]; then
  notes="$(find "$VAULT/01_проекты" -name '*.md' 2>/dev/null | wc -l | tr -d ' ')"
  ok "хранилище доступно, заметок: $notes"
else
  fail "нет хранилища: $VAULT/01_проекты"
fi
echo

echo "-- 9. Папки из STRUKTURA.md --"
for d in agent-marketolog direktor-marketinga marketing-otdel otdel-prodazh kontent-zavod \
         arhiv baza-znaniy tools; do
  [ -d "$d" ] && ok "папка: $d/" || warn "нет папки: $d/"
done
echo

echo "== Итог: OK $OK, WARN $WARN, FAIL $FAIL =="
if [ "$FAIL" -gt 0 ]; then
  echo "Есть поломки — смотреть FAIL выше. Карта: doktor/karta-neispravnostey.md"
  exit 1
fi
echo "Поломок нет. WARN — это «не сейчас», а не «сломано»."
exit 0
