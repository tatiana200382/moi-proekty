#!/bin/bash
# ВНИМАНИЕ: launchd не имеет доступа к папке на Рабочем столе без Full Disk Access.
# Без разрешения job падает с exit 126 («Operation not permitted»).
# Сначала: Системные настройки → Конфиденциальность → Полный доступ к диску → + → /bin/bash.
# Затем: I_HAVE_FDA=1 ./install_launchd_fda.sh
# Штатный способ без этого — start_autonomy.sh (через Терминал).
set -eu

if [ "${I_HAVE_FDA:-}" != "1" ]; then
  echo "Не устанавливаю: нужен Full Disk Access для /bin/bash."
  echo "Без него используйте ./otdel-prodazh/tools/start_autonomy.sh"
  exit 1
fi

ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
LABEL="com.silversong.sales"
PLIST="$HOME/Library/LaunchAgents/$LABEL.plist"
UID_NUM="$(id -u)"
RUN="$ROOT/otdel-prodazh/tools/run.sh"
LOG_DIR="$ROOT/otdel-prodazh/runtime/logs"
mkdir -p "$LOG_DIR" "$HOME/Library/LaunchAgents"

chmod +x "$RUN"

cat > "$PLIST" <<PLIST_EOF
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
  <key>Label</key>
  <string>$LABEL</string>
  <key>ProgramArguments</key>
  <array>
    <string>/bin/bash</string>
    <string>$RUN</string>
  </array>
  <key>WorkingDirectory</key>
  <string>$ROOT</string>
  <key>StartInterval</key>
  <integer>300</integer>
  <key>RunAtLoad</key>
  <true/>
  <key>ProcessType</key>
  <string>Background</string>
  <key>EnvironmentVariables</key>
  <dict>
    <key>PATH</key>
    <string>/usr/local/bin:/opt/homebrew/bin:/usr/bin:/bin:/usr/sbin:/sbin</string>
    <key>LANG</key>
    <string>ru_RU.UTF-8</string>
  </dict>
  <key>StandardOutPath</key>
  <string>$LOG_DIR/launchd.out.log</string>
  <key>StandardErrorPath</key>
  <string>$LOG_DIR/launchd.err.log</string>
</dict>
</plist>
PLIST_EOF

launchctl bootout "gui/$UID_NUM" "$PLIST" 2>/dev/null || true
launchctl bootstrap "gui/$UID_NUM" "$PLIST"
launchctl enable "gui/$UID_NUM/$LABEL" 2>/dev/null || true
launchctl kickstart -k "gui/$UID_NUM/$LABEL"

echo "Автозапуск установлен: $LABEL"
echo "Проверка: launchctl print gui/$UID_NUM/$LABEL | head -20"
echo "Логи:    $LOG_DIR/run.log"
