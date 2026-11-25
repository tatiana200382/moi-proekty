#!/bin/bash
# Двусторонняя синхронизация рабочей папки: Мак <-> сервер.
# Новее — побеждает, удаления не переносятся. Тяжёлое и симлинки — отдельно.
set -u
LOCAL="/Users/tatiana/Desktop/Обучение ИИ/proekty/Мои проекты"
SECRET="/Users/tatiana/Desktop/Обучение ИИ/Секретарь"
REMOTE="root@2.31.104.44:/root/workspace"
KEY="$HOME/.ssh/id_ed25519_server"
SSH="ssh -i $KEY -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null"
OPTS=(-az --update --timeout=120
      --exclude '.git' --exclude 'node_modules' --exclude '.DS_Store'
      --exclude 'arhiv/' --exclude 'agent-marketolog/' --exclude 'ii-marketolog/'
      --exclude 'obsidian/' --exclude 'sekretar' --exclude 'generated_images/'
      --exclude '*.zip' --exclude '*.pdf'
      -e "$SSH")

echo "== Мак → сервер"
rsync "${OPTS[@]}" "$LOCAL/" "$REMOTE/" || exit 1

echo "== секретарь (отдельная папка, копируем содержимое)"
rsync -az --update --timeout=120 --exclude '.git' -e "$SSH" "$SECRET/" "$REMOTE/sekretar/" || exit 1

echo "== сервер → Мак"
rsync "${OPTS[@]}" "$REMOTE/" "$LOCAL/" || exit 1
rsync -az --update --timeout=120 --exclude '.git' -e "$SSH" "$REMOTE/sekretar/" "$SECRET/" || exit 1

echo "== готово: $(date '+%H:%M:%S')"
