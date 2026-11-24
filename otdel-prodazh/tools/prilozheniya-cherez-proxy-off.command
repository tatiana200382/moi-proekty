#!/bin/bash
# Выключает системный прокси — нужен для Авито (российский IP).
SERV="Wi-Fi"   # сеть, через которую работает Mac
networksetup -setwebproxystate "$SERV" off
networksetup -setsecurewebproxystate "$SERV" off
echo "прокси выключен для сети «$SERV»"
