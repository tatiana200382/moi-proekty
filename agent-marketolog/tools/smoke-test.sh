#!/bin/bash
# Проверка всех инструментов Вовы. Ничего не публикует и не меняет.
# Запуск: ./tools/smoke-test.sh
cd "$(dirname "$0")/.." || exit 1
ROOT="$(pwd)"
PROJ="$ROOT/.."
PY=/Users/tatiana/.dsh/dsh-runtimes/dsh-primary-runtime/dependencies/python/bin/python3
NODE=/usr/local/bin/node
PASS=0; FAIL=0
ok(){ printf "%-34s OK   %s\n" "$1" "$2"; PASS=$((PASS+1)); }
no(){ printf "%-34s ПРОВАЛ %s\n" "$1" "$2"; FAIL=$((FAIL+1)); }

# 1. Chrome под управлением
if curl -s --max-time 3 http://127.0.0.1:9224/json/version | grep -q Browser; then
  ok "Chrome отладка 9224" "отвечает"
else no "Chrome отладка 9224" "порт не отвечает"; fi

# 2–3. Avito и ВК открыты (если вкладки нет — открываем)
curl -s --max-time 3 http://127.0.0.1:9224/json/list | grep -q avito.ru || curl -s -X PUT "http://127.0.0.1:9224/json/new?https://www.avito.ru/profile/items" >/dev/null
curl -s --max-time 3 http://127.0.0.1:9224/json/list | grep -q vk.ru || curl -s -X PUT "http://127.0.0.1:9224/json/new?https://vk.ru/s_sflowers" >/dev/null
sleep 3
TABS=$(curl -s --max-time 3 http://127.0.0.1:9224/json/list | $PY -c "import json,sys;print(' '.join(t.get('url','') for t in json.load(sys.stdin) if t.get('type')=='page'))" 2>/dev/null)
echo "$TABS" | grep -q avito.ru && ok "Авито" "вкладка открыта" || no "Авито" "вкладки нет"
echo "$TABS" | grep -q vk.ru && ok "ВКонтакте" "вкладка открыта" || no "ВКонтакте" "вкладки нет"

# 4. Рендер HTML→PNG
if ./tools/render.sh templates/post-card.html /tmp/smoke.png 1080 1350 >/dev/null 2>&1 && [ -s /tmp/smoke.png ]; then
  ok "Рендер HTML→PNG" "$(du -h /tmp/smoke.png | cut -f1)"
else no "Рендер HTML→PNG" "картинка не собралась"; fi

# 5. Фото и Pillow
$PY - <<'PYEOF' && ok "Обработка фото (Pillow)" "чтение и запись работают" || no "Обработка фото (Pillow)" "ошибка"
from PIL import Image
import glob
p = sorted(glob.glob("foto/bukety-arhiv/*.jpg"))[0]
img = Image.open(p); img.resize((200,200)).save("/tmp/smoke-photo.jpg")
PYEOF

# 6. Генератор фида Авито
if $PY tools/avito-feed.py templates/avito-tovary.csv /tmp/smoke-feed.xml >/dev/null 2>&1 && grep -q "<Ads" /tmp/smoke-feed.xml; then
  ok "Фид для Авито" "$(grep -c "<Ad>" /tmp/smoke-feed.xml) объявления"
else no "Фид для Авито" "не собрался"; fi

# 7. Git
if git -C "$PROJ" status --short >/dev/null 2>&1; then
  ok "Git" "ветка $(git -C "$PROJ" branch --show-current)"
else no "Git" "репозиторий не отвечает"; fi

# 8. GitHub API
if curl -s --max-time 5 https://api.github.com/rate_limit | grep -q remaining; then
  ok "GitHub API" "доступен"
else no "GitHub API" "нет ответа или VPN"; fi

# 9. Голос
if say -v Milena -o /tmp/smoke.aiff "проверка" 2>/dev/null && [ -s /tmp/smoke.aiff ]; then
  ok "Голос" "синтез записан"
else no "Голос" "say не отработал"; fi

# 10. Навыки
N=$(ls skills/*.md 2>/dev/null | wc -l | tr -d ' ')
[ "$N" -ge 8 ] && ok "Навыки" "$N файлов" || no "Навыки" "только $N файлов"

# 11. Роль проверяющего
[ -f reviewer.md ] && ok "Проверяющий" "роль на месте" || no "Проверяющий" "нет reviewer.md"

echo
echo "Итог: OK $PASS, провалов $FAIL"
[ "$FAIL" -eq 0 ]
