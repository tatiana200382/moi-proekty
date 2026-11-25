#!/bin/bash
# Полная проверка цикла «тревога → лечение → проверка → запись» на изолированном юните.
# Ничего рабочего не трогает: создаёт тестовый юнит doktor-probe и роняет его.
#
# Использование: doktor/tools/proverka-cikla.sh [число циклов]
# Требует: ssh-ключ и доступ root на сервере (как у сторожа).

set -uo pipefail
CYCLES="${1:-5}"
HOST="${DOKTOR_HOST:-root@2.31.104.44}"
KEY="${DOKTOR_KEY:-$HOME/.ssh/id_ed25519_server}"
SSH_OPTS=(-o BatchMode=yes -o ConnectTimeout=10 -o StrictHostKeyChecking=no
          -o UserKnownHostsFile=/dev/null -i "$KEY")

ssh_run() { ssh "${SSH_OPTS[@]}" "$HOST" "$1" 2>/dev/null; }

echo "== Проверка цикла Доктора: $CYCLES циклов =="
echo "Сервер: $HOST"
echo

ssh_run 'printf "[Unit]\nDescription=Test probe for Doktor\n[Service]\nType=simple\nExecStart=/bin/sleep infinity\n[Install]\nWantedBy=multi-user.target\n" > /etc/systemd/system/doktor-probe.service
systemctl daemon-reload; systemctl start doktor-probe; echo "тестовый юнит поднят"'

PASS=0; FAILN=0
for i in $(seq 1 "$CYCLES"); do
  before=$(ssh_run 'wc -l < /var/lib/doktor/actions.log 2>/dev/null || echo 0')
  out=$(ssh_run 'systemctl stop doktor-probe
DOKTOR_UNITS="ssh,dsh-web,doktor-probe" python3 /opt/doktor/storozh.py --fix --no-alert; echo "RC=$?"')
  rc=$(printf '%s' "$out" | grep -o 'RC=[0-9]*' | cut -d= -f2)
  summary=$(printf '%s' "$out" | grep 'Итог:' | sed 's/^.*Итог:/Итог:/')
  healed=$(printf '%s' "$out" | grep -A1 'Лечение:' | tail -1 | sed 's/^ *//')
  active=$(ssh_run 'systemctl is-active doktor-probe')
  after=$(ssh_run 'wc -l < /var/lib/doktor/actions.log 2>/dev/null || echo 0')
  new_actions=$((after - before))

  if [ "$active" = "active" ] && [ "$rc" = "0" ] && [ "$new_actions" -ge 1 ]; then
    PASS=$((PASS+1)); verdict="ПРОЙДЕН"
  else
    FAILN=$((FAILN+1)); verdict="ПРОВАЛ"
  fi

  echo "цикл $i: $verdict"
  echo "  $summary"
  echo "  лечение: ${healed:-нет строки}"
  echo "  юнит: $active · новых записей в журнале действий: $new_actions · код выхода: $rc"
done

echo
echo "== Пауза и запрет вне списка =="
pause=$(ssh_run 'touch /etc/doktor/PAUSE; systemctl stop doktor-probe
DOKTOR_UNITS="ssh,dsh-web,doktor-probe" python3 /opt/doktor/storozh.py --fix --no-alert 2>&1 | grep -A1 "Лечение:" | tail -1; rm -f /etc/doktor/PAUSE')
echo "пауза: $(printf '%s' "$pause" | sed 's/^ *//')"

ssh_run 'systemctl stop doktor-probe; rm -f /etc/systemd/system/doktor-probe.service; systemctl daemon-reload' >/dev/null
echo "тестовый юнит убран"

echo
echo "== Итог: пройдено $PASS из $CYCLES, провалов $FAILN =="
[ "$FAILN" -eq 0 ]
