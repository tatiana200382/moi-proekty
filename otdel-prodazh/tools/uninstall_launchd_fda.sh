#!/bin/bash
# Снимает автозапуск отдела продаж.
set -eu
LABEL="com.silversong.sales"
PLIST="$HOME/Library/LaunchAgents/$LABEL.plist"
UID_NUM="$(id -u)"
launchctl bootout "gui/$UID_NUM" "$PLIST" 2>/dev/null || true
rm -f "$PLIST"
echo "Автозапуск снят: $LABEL"
