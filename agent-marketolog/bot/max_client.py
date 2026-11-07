"""Клиент MAX Bot API. Токен — только в файле вне проекта.

Токен: ~/.config/max-bot/token (одна строка). Права 600.
ID чата: ~/.config/max-bot/chat_id — узнаётся командой discover-chat.

Документация: https://dev.max.ru/docs-api
Токен передаётся заголовком Authorization, chat_id — параметром запроса.
API использует сертификат Минцифры; его корневые сертификаты лежат в bot/certs/.
"""
import json
import os
import ssl
import stat
import sys
import urllib.error
import urllib.parse
import urllib.request

BASE = "https://platform-api2.max.ru"
CONFIG_DIR = os.path.expanduser("~/.config/max-bot")
TOKEN_FILE = os.path.join(CONFIG_DIR, "token")
CHAT_FILE = os.path.join(CONFIG_DIR, "chat_id")
LOCAL_CHAT_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "chat_id")
LOCAL_CA = os.path.join(os.path.dirname(os.path.abspath(__file__)), "certs", "max-ca.pem")
USER_CA = os.path.join(CONFIG_DIR, "ca.pem")
CA_URLS = [
    "https://gu-st.ru/content/lending/russian_trusted_root_ca_pem.crt",
    "https://gu-st.ru/content/lending/russian_trusted_sub_ca_pem.crt",
]


class MaxError(RuntimeError):
    pass


def _ca_file():
    for path in (os.environ.get("MAX_CA_BUNDLE"), USER_CA, LOCAL_CA):
        if path and os.path.exists(path):
            return path
    return None


def _context():
    ctx = ssl.create_default_context()
    ca = _ca_file()
    if ca:
        try:
            ctx.load_verify_locations(cafile=ca)
        except ssl.SSLError as e:
            raise MaxError(f"не читается файл сертификатов {ca}: {e}")
    return ctx


def token():
    if not os.path.exists(TOKEN_FILE):
        raise MaxError(f"нет файла с токеном: {TOKEN_FILE}")
    mode = stat.S_IMODE(os.stat(TOKEN_FILE).st_mode)
    if mode & 0o077:
        print(f"внимание: у {TOKEN_FILE} права {mode:o}, нужно 600", file=sys.stderr)
    with open(TOKEN_FILE, encoding="utf-8") as f:
        value = f.read().strip()
    if len(value) < 10:
        raise MaxError("токен пустой или слишком короткий")
    return value


def token_exists() -> bool:
    return os.path.exists(TOKEN_FILE) and os.path.getsize(TOKEN_FILE) > 10


def chat_id() -> str:
    for path in (CHAT_FILE, LOCAL_CHAT_FILE):
        if os.path.exists(path):
            with open(path, encoding="utf-8") as f:
                value = f.read().strip()
            if value:
                return value
    raise MaxError("нет ID чата. Добавьте бота в чат, напишите в нём и запустите discover-chat")


def call(method, path, payload=None, params=None, timeout=30):
    url = BASE + path
    if params:
        url += "?" + urllib.parse.urlencode(params)
    data = json.dumps(payload).encode() if payload is not None else None
    req = urllib.request.Request(
        url,
        data=data,
        method=method,
        headers={
            "Authorization": token(),
            "Content-Type": "application/json",
        },
    )
    try:
        with urllib.request.urlopen(req, timeout=timeout, context=_context()) as resp:
            raw = resp.read().decode()
            return json.loads(raw) if raw else {}
    except urllib.error.HTTPError as e:
        detail = e.read().decode(errors="replace")
        try:
            body = json.loads(detail)
            message = body.get("message") or body.get("code") or detail
        except ValueError:
            message = detail[:300]
        raise MaxError(f"MAX API {e.code}: {message}")
    except urllib.error.URLError as e:
        reason = e.reason
        if isinstance(reason, ssl.SSLError) or "CERTIFICATE_VERIFY" in str(reason):
            raise MaxError(
                "MAX API: не доверен сертификат Минцифры. "
                "Запустите python3 max_client.py trust или укажите MAX_CA_BUNDLE"
            )
        raise MaxError(f"MAX API недоступен: {reason}")


def me():
    return call("GET", "/me")


def send(chat_id_value, text):
    text = text.strip()
    if not text:
        raise MaxError("пустой текст")
    if len(text) > 4000:
        raise MaxError(f"текст {len(text)} символов, максимум 4000")
    return call("POST", "/messages", {"text": text}, params={"chat_id": chat_id_value})


def updates(marker=None, limit=100, timeout=5):
    params = {"limit": limit, "timeout": timeout}
    if marker:
        params["marker"] = marker
    return call("GET", "/updates", params=params, timeout=timeout + 15)


def _chat_from_update(update):
    """Достаёт chat_id группового чата из события. Личные диалоги с ботом не берём."""
    if update.get("is_channel"):
        return None
    chat_id_value = update.get("chat_id")
    chat_type = update.get("chat_type")
    message = update.get("message") or {}
    recipient = message.get("recipient") or {}
    chat_id_value = chat_id_value or recipient.get("chat_id")
    chat_type = chat_type or recipient.get("chat_type")
    if chat_id_value and chat_type in (None, "chat"):
        return str(chat_id_value)
    return None


def discover_chat():
    """Ищет chat_id в событиях бота и сохраняет его. Нужно одно сообщение боту в чате."""
    data = updates(timeout=3)
    found = []
    for update in data.get("updates", []):
        cid = _chat_from_update(update)
        if cid and cid not in found:
            found.append(cid)
    if not found:
        raise MaxError(
            "в событиях нет группового чата. Добавьте бота в чат «Заявки», "
            "напишите в нём любое сообщение и повторите"
        )
    cid = found[-1]
    saved = None
    for path in (CHAT_FILE, LOCAL_CHAT_FILE):
        try:
            os.makedirs(os.path.dirname(path), exist_ok=True)
            with open(path, "w", encoding="utf-8") as f:
                f.write(cid + "\n")
            os.chmod(path, 0o600)
            saved = path
            break
        except OSError:
            continue
    if saved:
        print(f"chat_id сохранён: {saved}")
    else:
        print(f"chat_id: {cid} (сохранить не удалось — впишите вручную)")
    return cid


def trust():
    """Скачивает корневые сертификаты Минцифры в ~/.config/max-bot/ca.pem."""
    chunks = []
    for url in CA_URLS:
        with urllib.request.urlopen(url, timeout=30) as resp:
            pem = resp.read().decode()
        chunks.append(pem.replace("\r\n", "\n").strip() + "\n")
    os.makedirs(CONFIG_DIR, exist_ok=True)
    with open(USER_CA, "w", encoding="utf-8") as f:
        f.write("\n".join(chunks))
    os.chmod(USER_CA, 0o644)
    print(f"сертификаты сохранены: {USER_CA}")


def main():
    cmd = sys.argv[1] if len(sys.argv) > 1 else "me"
    try:
        if cmd == "me":
            print(json.dumps(me(), ensure_ascii=False, indent=1))
        elif cmd == "send" and len(sys.argv) >= 4:
            print(json.dumps(send(sys.argv[2], sys.argv[3]), ensure_ascii=False)[:400])
        elif cmd == "send-file" and len(sys.argv) >= 4:
            with open(sys.argv[3], encoding="utf-8") as f:
                text = f.read()
            print(json.dumps(send(sys.argv[2], text), ensure_ascii=False)[:400])
        elif cmd == "updates":
            marker = sys.argv[2] if len(sys.argv) > 2 else None
            data = updates(marker=marker, timeout=3)
            print(json.dumps(data, ensure_ascii=False)[:1500])
        elif cmd == "discover-chat":
            discover_chat()
        elif cmd == "trust":
            trust()
        else:
            print("команды: me | send <chat_id> <текст> | send-file <chat_id> <файл> | "
                  "updates [marker] | discover-chat | trust")
    except MaxError as e:
        print(f"ошибка: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
