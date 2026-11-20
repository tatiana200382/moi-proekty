#!/bin/bash
# Настройка сна Mac: экран гаснет через 10 минут, сон через 20.
# Запускать двойным кликом; спросит пароль администратора.
echo "Настраиваю сон: экран 10 мин, сон 20 мин…"
osascript -e 'do shell script "pmset -a displaysleep 10 sleep 20 womp 0 powernap 0" with administrator privileges'
echo
echo "Готово. Текущие настройки:"
pmset -g | grep -E "displaysleep|^ sleep|womp|powernap"
