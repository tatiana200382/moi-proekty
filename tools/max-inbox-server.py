#!/usr/bin/env python3
"""Читает ответы флористов из чата MAX и отправляет их клиентам (с сервера).

Формат сообщения: <номер> <текст>   (номер — цифры; ВК — peer id)
"""
import hashlib, json, os, pathlib, re, subprocess, sys, time

BASE = pathlib.Path.home() / "sales"
sys.path.insert(0, str(BASE / "agent-marketolog" / "bot"))
import max_client  # noqa: E402

STATE = BASE / "otdel-prodazh" / "runtime" / "max-inbox-server.json"
PATTERN = re.compile(r"^#?([A-Za-z0-9_~\-]{6,})\s*(?:ответ|otvet)?\s*[:\-]?\s*(.+)$", re.I | re.S)
MAX_RE = re.compile(r"^#?max:(\d{5,})\s+(.+)$", re.I | re.S)
SEND_VK = BASE / "tools" / "vk-send-server.py"
PY_BIN = str(pathlib.Path.home() / "avito-bot" / "venv" / "bin" / "python")


def load_state():
    if STATE.exists():
        try: return json.loads(STATE.read_text())
        except Exception: pass
    return {"marker": None}


def save_state(st):
    STATE.parent.mkdir(parents=True, exist_ok=True)
    STATE.write_text(json.dumps(st, ensure_ascii=False))


def send_direct(channel: str, text: str) -> int:
    """Отправить ответ клиенту так же, как это делает бот из чата заявок."""
    is_vk = channel.isdigit()
    if is_vk:
        proc = subprocess.run([PY_BIN, str(SEND_VK), channel, text],
                              capture_output=True, text=True, timeout=180)
        ok = "ОТПРАВЛЕНО" in (proc.stdout or "")
        where = "ВКонтакте"
    else:
        proc = subprocess.run(["xvfb-run", "-a", "-s", "-screen 0 1710x1107x24",
                               PY_BIN, str(BASE / "tools" / "avito-send-xvfb.py"), channel, text],
                              capture_output=True, text=True, timeout=300)
        ok = '{"hit":true}' in (proc.stdout or "").replace(" ", "")
        where = "Авито"
    print(("OK " if ok else "FAIL ") + where, (proc.stdout or proc.stderr).strip()[:160])
    try:
        if ok:
            notify_author(None,
                            f"✅ Отправлено в {where} · {channel[:14]}…\n{text[:200]}")
        else:
            notify_author(None,
                            f"⚠️ Не отправлено в {where} · {channel[:14]}…\n{(proc.stdout or proc.stderr)[:150]}")
    except Exception as e:
        print("не смог уведомить чат:", e)
    return 0 if ok else 1


def report_sent(where: str, code: str, client: str) -> str:
    """Вид отчёта в боте заявок: ✅ Авито 8151871 Иринка Гавак."""
    return f"✅ {where} {code} {client}".strip()


def remember_reply(code: str, text: str) -> None:
    """Сохраняем наш ответ в заявке: карточка покажет «ответ магазина»."""
    path = BASE / "otdel-prodazh" / "runtime" / "state.json"
    try:
        st = json.loads(path.read_text())
    except Exception:
        return
    for k, v in st.get("leads", {}).items():
        if str(v.get("code") or "") == str(code):
            v["our_reply"] = text[:400]
            v["staff_replied"] = True
            v["status"] = "in_work"
    path.write_text(json.dumps(st, ensure_ascii=False, indent=1))


def chat_of_update(up: dict, msg: dict):
    cid = up.get("chat_id") or (msg.get("recipient") or {}).get("chat_id")
    ctype = up.get("chat_type") or (msg.get("recipient") or {}).get("chat_type")
    return str(cid or ""), ctype


def sender_name(sender: dict, author_id) -> str:
    name = " ".join(x for x in (sender.get("first_name"), sender.get("last_name")) if x).strip()
    return name or str(sender.get("username") or "") or str(author_id)


def mirror_to_chat(up: dict, msg: dict, sender: dict, author_id, code: str, where: str, text: str) -> None:
    """Личный ответ сотрудника показываем в группе «Заявки», как обычное сообщение."""
    cid, _ = chat_of_update(up, msg)
    if cid.startswith("-"):
        return
    try:
        group = max_client.chat_id()
        if not group:
            return
        who = sender_name(sender, author_id)
        max_client.send(group, f"💬 {who} · {where} · заявка {code}\n{text[:400]}")
        print("переслано в чат:", who, code)
    except Exception as e:
        print("не смог переслать в чат:", e)


def notify_author(author_id, text: str) -> None:
    """Отчёт об отправке — только в личный чат бота с автором команды."""
    try:
        if author_id:
            max_client.send_user(int(author_id), text)
        else:
            print("отчёт без автора:", text[:160].replace("\n", " "))
    except Exception as e:
        print("не смог отправить отчёт:", e)


def lead_code(v: dict) -> str:
    """Номер заявки: сохранённый в state или вычисленный (старые карточки)."""
    code = str(v.get("code") or "")
    if code:
        return code
    seed = f"{v.get('source')}|{v.get('external_id')}|{v.get('client')}"
    return str(int(hashlib.sha1(seed.encode()).hexdigest(), 16) % 9000000 + 1000000)


def resolve_code(code: str):
    """Короткий номер заявки → (канал, адрес, источник)."""
    state_path = BASE / "otdel-prodazh" / "runtime" / "state.json"
    try:
        st = json.loads(state_path.read_text())
    except Exception:
        return None
    for key, v in st.get("leads", {}).items():
        if lead_code(v) != code:
            continue
        src = (v.get("source") or "").lower()
        ext = str(v.get("external_id") or "")
        if src == "vk":
            peer = ext.split(":")[0]
            if peer.isdigit():
                return ("vk", peer, v)
        elif src == "avito":
            if ext:
                return ("avito", ext, v)
        elif src == "max":
            uid = ext.split(":")[-1]
            if uid.isdigit():
                return ("max", uid, v)
        elif src == "yandex":
            return ("yandex", "", v)
    return None


def once() -> int:
    st = load_state()
    data = max_client.updates(marker=st.get("marker"), limit=50, timeout=5)
    handled = 0
    for up in data.get("updates", []):
        msg = up.get("message") or {}
        body = (msg.get("body") or {}).get("text") or ""
        sender = msg.get("sender") or {}
        author_id = sender.get("user_id")
        if sender.get("is_bot"):
            continue
        short = re.match(r"^#?(\d{6,8})\s+(.+)$", body.strip(), re.S)
        if short:
            found = resolve_code(short.group(1))
            text = short.group(2).strip()
            if not found:
                print("номер не найден:", short.group(1))
            else:
                kind, target, lead = found
                if kind == "yandex":
                    notify_author(author_id, f"⚠️ Заявка {short.group(1)} — с Яндекс.Карт, отвечать нужно звонком на {lead.get('contact') or 'номер в карточке'}")
                else:
                    code_argv = target if kind != "max" else f"max:{target}"
                    proc = subprocess.run([PY_BIN, str(pathlib.Path(__file__)), "--send", code_argv, text],
                                          capture_output=True, text=True, timeout=400)
                    ok = "OK" in (proc.stdout or "")
                    if ok:
                        remember_reply(short.group(1), text)
                    where = "ВКонтакте" if kind == "vk" else "Авито"
                    detail = (proc.stdout or proc.stderr or "").strip()[:180]
                    notify_author(author_id,
                                  (f"✅ Отправлено в {where} · {short.group(1)}\n{text[:200]}" if ok
                                   else f"⚠️ Не отправлено в {where} · {short.group(1)}\n{detail}"))
                    if ok:
                        mirror_to_chat(up, msg, sender, author_id, short.group(1), where, text)
                    print("передано в отправку:", kind, detail[:100])
            handled += 1
            continue
        mmax = MAX_RE.match(body.strip())
        if mmax:
            uid, text = mmax.group(1), mmax.group(2).strip()
            try:
                max_client.send_user(int(uid), text)
                notify_author(author_id, f"✅ Отправлено клиенту в MAX · {uid}\n{text[:200]}")
                print("OK MAX", uid)
            except Exception as e:
                print("FAIL MAX", uid, e)
            handled += 1
            continue
        m = PATTERN.match(body.strip())
        if not m:
            continue
        channel, text = m.group(1), m.group(2).strip()
        is_vk = channel.isdigit()
        if not is_vk:
            proc = subprocess.run(["xvfb-run", "-a", "-s", "-screen 0 1710x1107x24",
                                   PY_BIN, str(BASE / "tools" / "avito-send-xvfb.py"), channel, text],
                                  capture_output=True, text=True, timeout=240)
            ok = '{"hit":true}' in (proc.stdout or "").replace(" ", "")
            print(("OK AVITO " if ok else "FAIL AVITO ") + channel, (proc.stdout or proc.stderr).strip()[:120])
            try:
                if ok:
                    notify_author(author_id, f"✅ Отправлено в Авито · {channel[:14]}…\n{text[:200]}")
                else:
                    notify_author(author_id, f"⚠️ Не отправлено в Авито · {channel[:14]}…\n{(proc.stdout or proc.stderr)[:150]}")
            except Exception as e:
                print("не смог уведомить чат:", e)
            handled += 1
            continue
        proc = subprocess.run([PY_BIN, str(SEND_VK), channel, text],
                              capture_output=True, text=True, timeout=180)
        ok = "ОТПРАВЛЕНО" in (proc.stdout or "")
        print(("OK " if ok else "FAIL ") + channel, (proc.stdout or proc.stderr).strip()[:120])
        try:
            if ok:
                notify_author(author_id, f"✅ Отправлено в ВКонтакте · {channel[:12]}…\n{text[:200]}")
                mirror_to_chat(up, msg, sender, author_id, channel[:12], "ВКонтакте", text)
            else:
                notify_author(author_id, f"⚠️ Не отправлено в ВК · {channel[:12]}…\n{(proc.stdout or proc.stderr)[:150]}")
        except Exception as e:
            print("не смог уведомить чат:", e)
        handled += 1
    if data.get("marker"):
        st["marker"] = data["marker"]
    save_state(st)
    print(f"апдейтов: {len(data.get('updates', []))}, ответов: {handled}")
    return handled


if __name__ == "__main__":
    if len(sys.argv) > 3 and sys.argv[1] == "--send":
        sys.exit(send_direct(sys.argv[2], " ".join(sys.argv[3:])))
    sys.exit(0 if once() >= 0 else 1)
