#!/bin/bash
# Двусторонняя синхронизация рабочей папки: Мак <-> сервер.
# Правило: какой файл новее, тот и побеждает. Удаления не переносятся.
# Тяжёлые папки (картинки, архивы) не синхронизируются — только рабочая часть.
set -u
LOCAL="/Users/tatiana/Desktop/Обучение ИИ/proekty/Мои проекты"
REMOTE="root@2.31.104.44:/root/workspace"
KEY="$HOME/.ssh/id_ed25519_server"
OPTS=(-az --update --timeout=120
      --exclude '.git' --exclude 'node_modules' --exclude '.DS_Store'
      --exclude 'arhiv/' --exclude 'agent-marketolog/' --exclude 'ii-marketolog/'
      --exclude 'obsidian/' --exclude 'generated_images/' --exclude '*.zip' --exclude '*.pdf'
      -e "ssh -i $KEY -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null")

echo "== Мак → сервер"
rsync "${OPTS[@]}" "$LOCAL/" "$REMOTE/" || exit 1
echo "== сервер → Мак"
rsync "${OPTS[@]}" "$REMOTE/" "$LOCAL/" || exit 1
echo "== готово: $(date '+%H:%M:%S')"
