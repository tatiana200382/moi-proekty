#!/bin/bash
# Полная проверка цикла «сбой → лечение → проверка → запись» на изолированном юните.
# Рабочие сервисы не трогаются: используется тестовый юнит doktor-probe и отдельные
# файлы состояния, чтобы не тратить лимит настоящих действий.
#
# Использование: doktor/tools/proverka-cikla.sh [число циклов]

set -uo pipefail
CYCLES="${1:-5}"
HOST="${DOKTOR_HOST:-root@2.31.104.44}"
KEY="${DOKTOR_KEY:-$HOME/.ssh/id_ed25519_server}"
SSH_OPTS=(-o BatchMode=yes -o ConnectTimeout=10 -o StrictHostKeyChecking=no
          -o UserKnownHostsFile=/dev/null -i "$KEY")
TEST_LOG=/tmp/doktor-test-actions.log
TEST_STATE=/tmp/doktor-test-state.json

run() { ssh "${SSH_OPTS[@]}" "$HOST" "$1" 2>/dev/null; }
probe() {
  run "DOKTOR_ACTIONS=$TEST_LOG DOKTOR_STATE=$TEST_STATE DOKTOR_MAX_ACTIONS=10 \
DOKTOR_UNITS=ssh,dsh-web,doktor-probe python3 /opt/doktor/storozh.py --fix --no-alert"
}

echo "== Проверка цикла Доктора: $CYCLES циклов =="
echo "Сервер: $HOST"
echo

run 'printf "[Unit]\nDescription=Test probe for Doktor\n[Service]\nType=simple\nExecStart=/bin/sleep infinity\n[Install]\nWantedBy=multi-user.target\n" > /etc/systemd/system/doktor-probe.service
systemctl daemon-reload; systemctl start doktor-probe; rm -f /tmp/doktor-test-actions.log /tmp/doktor-test-state.json
echo "тестовый юнит поднят"'

PASS=0; FAILED=0
for i in $(seq 1 "$CYCLES"); do
  before=$(run "wc -l < $TEST_LOG 2>/dev/null || echo 0")
  run 'systemctl stop doktor-probe'
  out=$(probe)
  rc=$?
  active=$(run 'systemctl is-active doktor-probe')
  after=$(run "wc -l < $TEST_LOG 2>/dev/null || echo 0")
  new_actions=$((after - before))
  summary=$(printf '%s' "$out" | grep 'Итог:' | sed 's/^.*Итог:/Итог:/')
  healed=$(printf '%s' "$out" | grep -A1 'Лечение:' | tail -1 | sed 's/^ *//')

  if [ "$active" = "active" ] && [ "$rc" = "0" ] && [ "$new_actions" -ge 1 ]; then
    PASS=$((PASS+1)); verdict="ПРОЙДЕН"
  else
    FAILED=$((FAILED+1)); verdict="ПРОВАЛ"
  fi

  echo "цикл $i: $verdict"
  echo "  ${summary:-нет строки итога}"
  echo "  лечение: ${healed:-нет строки}"
  echo "  юнит: $active · записей в журнале: +$new_actions · код выхода: $rc"
done

echo
echo "== Пауза =="
run 'touch /etc/doktor/PAUSE; systemctl stop doktor-probe'
pause_out=$(probe)
echo "  $(printf '%s' "$pause_out" | grep -A1 'Лечение:' | tail -1 | sed 's/^ *//')"
echo "  юнит после паузы: $(run 'systemctl is-active doktor-probe') (ожидается inactive)"
run 'rm -f /etc/doktor/PAUSE'

echo
echo "== Чужой юнит вне белого списка =="
run 'printf "[Unit]\nDescription=not allowed\n[Service]\nType=simple\nExecStart=/bin/sleep infinity\n" > /etc/systemd/system/test-other.service
systemctl daemon-reload; systemctl start test-other; systemctl stop test-other'
other_out=$(run "DOKTOR_ACTIONS=$TEST_LOG DOKTOR_STATE=$TEST_STATE DOKTOR_MAX_ACTIONS=10 DOKTOR_UNITS=ssh,dsh-web,test-other python3 /opt/doktor/storozh.py --fix --no-alert")
echo "  $(printf '%s' "$other_out" | grep -A1 'Лечение:' | tail -1 | sed 's/^ *//')"
echo "  test-other: $(run 'systemctl is-active test-other') (ожидается inactive)"

echo
echo "== Уборка тестовых юнитов =="
run 'systemctl stop doktor-probe test-other 2>/dev/null; rm -f /etc/systemd/system/doktor-probe.service /etc/systemd/system/test-other.service
rm -f /tmp/doktor-test-actions.log /tmp/doktor-test-state.json; systemctl daemon-reload'
echo "  тестовые юниты и файлы удалены"

echo
echo "== Итог: пройдено $PASS из $CYCLES, провалов $FAILED =="
[ "$FAILED" -eq 0 ]
