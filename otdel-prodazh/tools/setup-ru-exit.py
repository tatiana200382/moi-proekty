#!/usr/bin/env python3
"""Добавляет российский выход (VLESS) в Xray на немецком сервере.

Использование (на сервере):
    python3 setup-ru-exit.py "vless://UUID@HOST:PORT?type=tcp&security=reality&pbk=...&sid=...&sni=...&flow=xtls-rprx-vision#name"

Что делает:
 1. Копия /root/xray.json в /root/xray.json.bak-<время>
 2. Добавляет outbound "ru-exit" (VLESS+Reality) и локальный SOCKS 127.0.0.1:1081
 3. Правила маршрута: домены Авито/ВК/МАКС/Mail.ru → ru-exit, остальное — как было
 4. Проверяет конфиг (xray -test), перезапускает службу, тестирует avito через 1081
 5. При ошибке — откат из резервной копии
"""
import base64, json, shutil, subprocess, sys, time, urllib.parse, pathlib, datetime

CFG = pathlib.Path("/root/xray.json")
SOCKS_PORT = 1081
RU_DOMAINS = ["domain:avito.ru", "domain:avito.st", "domain:avito.com",
              "domain:vk.com", "domain:userapi.com", "domain:vk.me",
              "domain:max.ru", "domain:oneme.ru", "domain:mail.ru"]


def parse(uri):
    assert uri.startswith("vless://"), "нужна ссылка vless://"
    u = urllib.parse.urlsplit(uri)
    q = dict(urllib.parse.parse_qsl(u.query))
    return {
        "id": u.username, "host": u.hostname, "port": u.port or 443,
        "pbk": q.get("pbk", ""), "sid": q.get("sid", ""),
        "sni": q.get("sni") or q.get("host") or u.hostname,
        "flow": q.get("flow", ""), "fp": q.get("fp", "chrome"),
        "tag": (u.fragment or "ru-exit").strip() or "ru-exit",
    }


def main():
    if len(sys.argv) < 2:
        sys.exit("нужна ссылка vless://")
    p = parse(sys.argv[1])
    cfg = json.loads(CFG.read_text())
    backup = CFG.with_suffix(f".json.bak-{datetime.datetime.now():%Y%m%d-%H%M%S}")
    shutil.copy2(CFG, backup)

    out = {
        "tag": "ru-exit", "protocol": "vless",
        "settings": {"vnext": [{"address": p["host"], "port": p["port"],
            "users": [{"id": p["id"], "encryption": "none", "flow": p["flow"]}]}]},
        "streamSettings": {"network": "tcp", "security": "reality",
            "realitySettings": {"serverName": p["sni"], "publicKey": p["pbk"],
                "shortId": p["sid"], "fingerprint": p["fp"]}},
    }
    cfg["outbounds"] = [o for o in cfg.get("outbounds", []) if o.get("tag") != "ru-exit"] + [out]

    inb = {"tag": "local-socks", "listen": "127.0.0.1", "port": SOCKS_PORT,
           "protocol": "socks", "settings": {"auth": "noauth", "udp": False}}
    cfg["inbounds"] = [i for i in cfg.get("inbounds", []) if i.get("tag") != "local-socks"] + [inb]

    rules = [r for r in cfg.get("routing", {}).get("rules", [])
             if r.get("outboundTag") != "ru-exit"]
    rules.insert(0, {"type": "field", "domain": RU_DOMAINS, "outboundTag": "ru-exit"})
    cfg.setdefault("routing", {})["rules"] = rules
    cfg["routing"].setdefault("domainStrategy", "IPIfNonMatch")

    CFG.write_text(json.dumps(cfg, ensure_ascii=False, indent=2))
    test = subprocess.run(["/root/xray", "run", "-test", "-c", str(CFG)],
                          capture_output=True, text=True)
    if test.returncode != 0:
        shutil.copy2(backup, CFG)
        sys.exit("конфиг не прошёл проверку, откат:\n" + test.stderr[-800:])

    subprocess.run(["systemctl", "restart", "xray"], check=True)
    time.sleep(3)
    r = subprocess.run(["curl", "-s", "-m", "20", "--socks5-hostname",
                        f"127.0.0.1:{SOCKS_PORT}", "-o", "/dev/null",
                        "-w", "%{http_code}", "https://www.avito.ru/"],
                       capture_output=True, text=True)
    print(f"avito через российский выход: {r.stdout or '—'}")
    print(f"резервная копия: {backup}")


if __name__ == "__main__":
    main()
