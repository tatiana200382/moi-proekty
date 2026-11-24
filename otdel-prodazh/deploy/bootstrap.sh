#!/bin/bash
# Установка заявок на Linux-сервер (Debian/Ubuntu). Запускать на сервере от root.
# Что делает: ставит Python, Node, Chromium, git; клонирует репозиторий; создаёт systemd-службы.
set -euo pipefail

REPO="git@github.com:tatiana200382/moi-proekty.git"
DIR="/opt/silversong"
USER_NAME="${SUDO_USER:-root}"

echo "== 1. Пакеты"
apt-get update -y
apt-get install -y python3 python3-pip git curl unzip chromium chromium-driver ca-certificates

echo "== 2. Node 20"
if ! command -v node >/dev/null; then
  curl -fsSL https://deb.nodesource.com/setup_20.x | bash -
  apt-get install -y nodejs
fi

echo "== 3. Код"
mkdir -p "$DIR"
if [ ! -d "$DIR/.git" ]; then
  git clone "$REPO" "$DIR"
fi
chown -R "$USER_NAME":"$USER_NAME" "$DIR"

echo "== 4. Запрет сна"
systemctl mask sleep.target suspend.target hibernate.target hybrid-sleep.target || true

echo "== 5. Файлы доступа"
echo "Положите в $DIR/otdel-prodazh/runtime/: max-bot/.env, max-ca.pem, cookies Авито."
echo "Затем запустите: systemctl enable --now silversong-max silversong-run"

echo "Готово. Дальше — перенос cookie и проверка."
