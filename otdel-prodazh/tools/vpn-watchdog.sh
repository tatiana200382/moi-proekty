#!/bin/bash
# Сторож: если туннель не отвечает — выключает системный прокси, чтобы интернет не пропадал.
# Когда туннель вернулся — включает прокси обратно.
STATE=/tmp/vpn-watchdog.state
CUR=$(cat "$STATE" 2>/dev/null || echo on)

if curl -s -m 6 --socks5-hostname 127.0.0.1:1082 https://api.ipify.org >/dev/null 2>&1; then
  if [ "$CUR" != "on" ]; then
    networksetup -setsocksfirewallproxystate "Wi-Fi" on
    echo on > "$STATE"
  fi
else
  if [ "$CUR" != "off" ]; then
    networksetup -setsocksfirewallproxystate "Wi-Fi" off
    echo off > "$STATE"
  fi
  launchctl kickstart -k "gui/$(id -u)/ru.silversong.socks" >/dev/null 2>&1
fi
