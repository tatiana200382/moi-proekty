#!/bin/bash
# Настройка российского сервера: прокси только для немецкого сервера + проверка Авито.
# Запускать на новом сервере от root: bash setup-ru-node.sh
set -u
DE_IP="2.31.104.44"
UA="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36"
export DEBIAN_FRONTEND=noninteractive

echo "== 1. Обновление системы"
apt-get update -qq && apt-get upgrade -y -qq

echo "== 2. Пакеты"
apt-get install -y -qq squid curl ufw fail2ban apache2-utils >/dev/null

echo "== 3. Пользователь и пароль прокси"
PROXY_USER="silver"
PROXY_PASS=$(head -c 12 /dev/urandom | base64 | tr -dc 'A-Za-z0-9' | head -c 16)
htpasswd -bc /etc/squid/passwd "$PROXY_USER" "$PROXY_PASS" >/dev/null 2>&1

echo "== 4. Настройка squid (доступ только с $DE_IP)"
cat > /etc/squid/squid.conf <<EOF
auth_param basic program /usr/lib/squid/basic_ncsa_auth /etc/squid/passwd
auth_param basic realm Silversong RU exit
acl authenticated proxy_auth REQUIRED
acl german_server src $DE_IP
acl SSL_ports port 443
acl Safe_ports port 80 443
acl CONNECT method CONNECT
http_access deny !Safe_ports
http_access deny CONNECT !SSL_ports
http_access allow german_server authenticated
http_access deny all
http_port 3128
visible_hostname ru-exit-silversong
access_log /var/log/squid/access.log
EOF
systemctl restart squid
systemctl enable squid >/dev/null 2>&1

echo "== 5. Файрвол"
ufw --force reset >/dev/null 2>&1
ufw default deny incoming >/dev/null
ufw default allow outgoing >/dev/null
ufw allow 22/tcp >/dev/null
ufw allow from $DE_IP to any port 3128 proto tcp >/dev/null
ufw --force enable >/dev/null

echo "== 6. Проверка: Авито с этого адреса"
CODE=$(curl -s -m 30 -A "$UA" -o /tmp/avito.html -w "%{http_code}" https://www.avito.ru/ || echo "000")
SIZE=$(stat -c %s /tmp/avito.html 2>/dev/null || echo 0)
echo "Авито: код $CODE, размер $SIZE байт"
if [ "$CODE" = "200" ]; then
  echo "РЕЗУЛЬТАТ: адрес подходит ✅"
else
  echo "РЕЗУЛЬТАТ: Авито не пускает (код $CODE) ❌"
fi

echo "== 7. Итог"
echo "IP: $(curl -s -m 10 https://api.ipify.org)"
echo "Прокси: http://$PROXY_USER:$PROXY_PASS@$(curl -s -m 10 https://api.ipify.org):3128"
echo "Доступ только с $DE_IP"
