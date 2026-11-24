#!/bin/bash
# Настройка: WireGuard + squid (HTTP-прокси с паролем) + ufw
set -euo pipefail
export DEBIAN_FRONTEND=noninteractive

echo "== пакеты"
apt-get update -y
apt-get install -y wireguard wireguard-tools ufw squid apache2-utils curl jq qrencode

echo "== WireGuard"
WG=/etc/wireguard; mkdir -p "$WG"; chmod 700 "$WG"; cd "$WG"
[ -f server.key ] || wg genkey | tee server.key | wg pubkey > server.pub
[ -f client.key ] || wg genkey | tee client.key | wg pubkey > client.pub
SPRIV=$(cat server.key); SPUB=$(cat server.pub); CPRIV=$(cat client.key); CPUB=$(cat client.pub)
SRV_IP=$(curl -s -4 ifconfig.co)

cat > wg0.conf <<EOF
[Interface]
Address = 10.8.0.1/24
ListenPort = 51820
PrivateKey = $SPRIV
PostUp   = iptables -A FORWARD -i wg0 -j ACCEPT; iptables -t nat -A POSTROUTING -o $(ip route get 1.1.1.1 | awk '{print $5; exit}') -j MASQUERADE
PostDown = iptables -D FORWARD -i wg0 -j ACCEPT; iptables -t nat -D POSTROUTING -o $(ip route get 1.1.1.1 | awk '{print $5; exit}') -j MASQUERADE

[Peer]
PublicKey = $CPUB
AllowedIPs = 10.8.0.2/32
EOF
chmod 600 wg0.conf
echo "net.ipv4.ip_forward=1" > /etc/sysctl.d/99-wg.conf
sysctl -p /etc/sysctl.d/99-wg.conf >/dev/null
systemctl enable --now wg-quick@wg0

cat > /root/client-mac.conf <<EOF
[Interface]
PrivateKey = $CPRIV
Address = 10.8.0.2/32
DNS = 1.1.1.1, 8.8.8.8

[Peer]
PublicKey = $SPUB
Endpoint = $SRV_IP:51820
AllowedIPs = 0.0.0.0/0
PersistentKeepalive = 25
EOF

echo "== squid (прокси с паролем)"
PUSER=silver
PPASS=$(head -c 32 /dev/urandom | base64 | tr -dc 'A-Za-z0-9' | head -c 16)
htpasswd -bc /etc/squid/passwd "$PUSER" "$PPASS" >/dev/null

cat > /etc/squid/squid.conf <<EOF
http_port 3128
auth_param basic program /usr/lib/squid/basic_ncsa_auth /etc/squid/passwd
auth_param basic realm proxy
acl authenticated proxy_auth REQUIRED
http_access allow authenticated
http_access deny all
visible_hostname silversong
cache deny all
EOF
systemctl restart squid
systemctl enable squid >/dev/null

echo "== файрвол"
ufw --force reset >/dev/null
ufw default deny incoming >/dev/null
ufw default allow outgoing >/dev/null
ufw allow 22/tcp >/dev/null
ufw allow 51820/udp >/dev/null
ufw allow 3128/tcp >/dev/null
ufw --force enable >/dev/null

echo
echo "==== ГОТОВО ===="
echo "IP сервера:      $SRV_IP"
echo "Прокси:          $PUSER:$PPASS@$SRV_IP:3128"
echo "Конфиг VPN:      /root/client-mac.conf"
echo "--- проверка выхода через прокси:"
curl -s -x "http://$PUSER:$PPASS@127.0.0.1:3128" https://ifconfig.co || true
echo
