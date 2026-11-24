#!/bin/bash
# Настройка немецкого сервера: WireGuard VPN + прокси + защита.
# Запуск на сервере от root: bash setup.sh
set -euo pipefail

echo "== 1. Обновление"
export DEBIAN_FRONTEND=noninteractive
apt-get update -y
apt-get -y upgrade
apt-get install -y wireguard wireguard-tools ufw fail2ban curl jq qrencode 3proxy

echo "== 2. Файрвол"
ufw --force reset
ufw default deny incoming
ufw default allow outgoing
ufw allow 22/tcp
ufw allow 51820/udp
ufw allow 3128/tcp
ufw --force enable

echo "== 3. WireGuard сервер"
WG_DIR=/etc/wireguard
mkdir -p "$WG_DIR"; chmod 700 "$WG_DIR"
cd "$WG_DIR"
[ -f server.key ] || wg genkey | tee server.key | wg pubkey > server.pub
SERVER_PRIV=$(cat server.key)
SERVER_PUB=$(cat server.pub)
SERVER_IP=$(curl -s -4 ifconfig.co)

[ -f client.key ] || wg genkey | tee client.key | wg pubkey > client.pub
CLIENT_PRIV=$(cat client.key)
CLIENT_PUB=$(cat client.pub)

cat > wg0.conf <<EOF
[Interface]
Address = 10.8.0.1/24
ListenPort = 51820
PrivateKey = $SERVER_PRIV
PostUp   = iptables -A FORWARD -i wg0 -j ACCEPT; iptables -t nat -A POSTROUTING -o eth0 -j MASQUERADE
PostDown = iptables -D FORWARD -i wg0 -j ACCEPT; iptables -t nat -D POSTROUTING -o eth0 -j MASQUERADE

[Peer]
PublicKey = $CLIENT_PUB
AllowedIPs = 10.8.0.2/32
EOF
chmod 600 wg0.conf

echo "net.ipv4.ip_forward=1" > /etc/sysctl.d/99-wg.conf
sysctl -p /etc/sysctl.d/99-wg.conf >/dev/null
systemctl enable --now wg-quick@wg0

cat > /root/client-mac.conf <<EOF
[Interface]
PrivateKey = $CLIENT_PRIV
Address = 10.8.0.2/32
DNS = 1.1.1.1, 8.8.8.8

[Peer]
PublicKey = $SERVER_PUB
Endpoint = $SERVER_IP:51820
AllowedIPs = 0.0.0.0/0
PersistentKeepalive = 25
EOF

echo "== 4. Прокси (3128, логин/пароль)"
PROXY_USER=silver
PROXY_PASS=$(head -c 18 /dev/urandom | base64 | tr -dc 'A-Za-z0-9' | head -c 16)
cat > /etc/3proxy/3proxy.cfg <<EOF
daemon
maxconn 200
nserver 1.1.1.1
nscache 65536
timeouts 1 5 30 60 180 1800 15 60
log /var/log/3proxy.log D
rotate 30
auth strong
users $PROXY_USER:CL:$PROXY_PASS
allow $PROXY_USER
proxy -p3128
EOF
systemctl enable --now 3proxy || (mkdir -p /etc/systemd/system/3proxy.service.d; echo ok)

echo "== 5. fail2ban"
systemctl enable --now fail2ban

echo
echo "==== ГОТОВО ===="
echo "Внешний IP:        $SERVER_IP"
echo "Прокси:            http://$PROXY_USER:$PROXY_PASS@$SERVER_IP:3128"
echo "WireGuard конфиг:  /root/client-mac.conf"
echo
echo "Проверка выхода:"
curl -s -x "http://$PROXY_USER:$PROXY_PASS@127.0.0.1:3128" https://ifconfig.co || echo "прокси проверьте вручную"
