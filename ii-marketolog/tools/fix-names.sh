#!/bin/bash
# Правит названия товаров в прайс-листе Яндекс.Бизнеса по парам "старое|новое".
set -u
NODE=/usr/local/bin/node
DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$DIR"

fix_one() {
  local old="$1" new="$2"
  sed "s|__OLD__|${old}|g" js/open-item.tpl.js > js/_open.js
  $NODE cdp.mjs evalfile js/_open.js 0 >/dev/null 2>&1
  sleep 2
  sed -e "s|__OLD__|${old}|g" -e "s|__NEW__|${new}|g" js/set-name.tpl.js > js/_set.js
  local res
  res=$($NODE cdp.mjs evalfile js/_set.js 0 2>&1 | head -1)
  sleep 4
  echo "$old → $new :: $res"
}

fix_one 'Букет Белых роз(80 см)' 'Букет белых роз (80 см)'
fix_one 'Букет цветов "Франузский поцелуй"' 'Букет цветов «Французский поцелуй»'
fix_one 'Цветы стабилизированные( сухоцветы) №1' 'Цветы стабилизированные (сухоцветы) №1'
fix_one 'подарочный набор №4' 'Подарочный набор №4'
fix_one 'Букет цветов " Океан"' 'Букет цветов «Океан»'
fix_one 'Букет цветов " Время любить"' 'Букет цветов «Время любить»'
fix_one 'Букет цветов "Аромат "' 'Букет цветов «Аромат»'
fix_one 'Букет цветов " Ароматы любви"' 'Букет цветов «Ароматы любви»'
