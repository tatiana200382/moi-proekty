"""Merge Telegram contacts, profiles and chat references with phone contacts."""
from common import DATA, TG_DIR

import json, io, re, os, collections

WS = str(DATA)
PHONE = os.path.join(WS, "people.json")
TGDIR = str(TG_DIR)
CHAT_REFS = str(TG_DIR / "chat_refs.json")
CHAT_NAME = "Рабочий чат"
OUT = str(DATA / "people_all.json")

SOCIAL = {
    "instagram.com": "Instagram", "instagr.am": "Instagram",
    "vk.com": "VK", "vk.ru": "VK", "vk.me": "VK",
    "youtube.com": "YouTube", "youtu.be": "YouTube",
    "t.me": "Telegram",
    "facebook.com": "Facebook", "fb.com": "Facebook",
    "tiktok.com": "TikTok", "dzen.ru": "Дзен", "zen.yandex.ru": "Дзен",
    "ok.ru": "OK", "linkedin.com": "LinkedIn", "threads.net": "Threads",
    "pinterest.com": "Pinterest", "rutube.ru": "Rutube",
    "wa.me": "WhatsApp", "whatsapp.com": "WhatsApp",
}
PORTFOLIO = ("behance.net", "dribbble.com", "portfolio", "taplink.cc", "taplink.ws",
             "notion.site", "notion.so", "readymag.com", "canva.com", "miro.com",
             "figma.com", "tilda.ws", "carrd.co", "bento.me", "linktr.ee")

URL_RE = re.compile(r"(?:https?://)?(?:[a-z0-9](?:[a-z0-9-]*[a-z0-9])?\.)+[a-z]{2,}(?:/[^\s,;|()\[\]<>\"']*)?", re.I)

def digits(s):
    d = re.sub(r"\D", "", s or "")
    if len(d) == 11 and d[0] in "78":
        d = d[1:]
    return d if len(d) >= 10 else ""

def norm(s):
    s = (s or "").lower().replace("ё", "е")
    s = re.sub(r"[^а-яa-z0-9\s]", " ", s)
    return re.sub(r"\s+", " ", s).strip()

def split_links(text, own_username=""):
    site = portfolio = channel = ""
    socials, seen = [], set()
    for m in URL_RE.finditer(text or ""):
        raw = m.group(0).strip().rstrip(".,;:)")
        host = re.sub(r"^https?://", "", raw, flags=re.I).split("/")[0].lower()
        if host.startswith("www."):
            host = host[4:]
        url = raw if raw.lower().startswith("http") else "https://" + raw
        if url in seen:
            continue
        seen.add(url)
        if host in ("t.me", "telegram.me"):
            handle = url.rstrip("/").split("/")[-1]
            if own_username and handle.lower() == own_username.lower():
                continue
            channel = channel or url
        elif host in SOCIAL:
            socials.append(f"{SOCIAL[host]}: {url}")
        elif any(p in host or p in url.lower() for p in PORTFOLIO):
            portfolio = portfolio or url
        else:
            site = site or url
    return site, portfolio, socials, channel

def load_profiles():
    prof = {}
    for pf in sorted(TG_DIR.glob("profiles_*.json")):
        try:
            data = json.load(io.open(pf, encoding="utf-8"))
        except Exception:
            continue
        if isinstance(data, dict):
            prof.update(data)
    return prof

def contact_records(profiles):
    """Records from all contact lists (any session name, including main)."""
    recs = []
    for path in sorted(TG_DIR.glob("contacts_*.json")):
        acc = path.stem[len("contacts_"):]
        try:
            contacts = json.load(io.open(path, encoding="utf-8"))
        except Exception:
            continue
        for c in contacts:
            p = profiles.get(f"{acc}:{c['id']}", {})
            recs.append({
                "key": f"id:{acc}:{c['id']}",
                "name": " ".join(x for x in (c.get("first_name", ""), c.get("last_name", "")) if x).strip(),
                "phone": c.get("phone", "") or "",
                "username": (c.get("username") or "").strip(),
                "bot": bool(c.get("bot")),
                "about": (p.get("about") or "").strip(),
                "channel": p.get("channel") or "",
                "chat": "",
                "snippet": "",
            })
    return recs

def chat_records():
    """Records from the working chat: users, channels and unresolved handles."""
    if not os.path.exists(CHAT_REFS):
        return []
    recs = []
    for r in json.load(io.open(CHAT_REFS, encoding="utf-8")):
        kind = r.get("kind")
        if kind == "User" and not r.get("bot"):
            name = " ".join(x for x in (r.get("first_name", ""), r.get("last_name", "")) if x).strip()
        elif kind == "Channel":
            name = (r.get("title") or "").strip()
        else:
            name = ""
        handle = (r.get("username") or r.get("handle") or "").strip()
        if not name and not handle:
            continue
        recs.append({
            "key": f"ref:{handle.lower()}",
            "name": name or handle,
            "phone": r.get("phone", "") or "",
            "username": handle,
            "bot": bool(r.get("bot")),
            "about": (r.get("about") or "").strip(),
            "channel": r.get("channel") or "",
            "chat": (r.get("chat") or CHAT_NAME).strip(),
            "snippet": (r.get("snippet") or "").strip(),
            "kind": kind,
        })
    return recs

def main():
    people = json.load(io.open(PHONE, encoding="utf-8"))
    profiles = load_profiles()

    by_phone, by_name, by_handle = {}, collections.defaultdict(list), {}
    for p in people:
        for ph in p["phones"]:
            d = digits(ph["num"])
            if d and d not in by_phone:
                by_phone[d] = p
        n = norm(p["name"])
        if n:
            by_name[n].append(p)
        for h in (p.get("tg_username") or "").split("; "):
            if h:
                by_handle[h.lower()] = p

    stats = collections.Counter()
    seen = set()

    for rec in contact_records(profiles) + chat_records():
        if rec["bot"]:
            stats["bot_skipped"] += 1
            continue
        if rec["key"] in seen:
            continue
        seen.add(rec["key"])

        uname = rec["username"]
        bio = rec["about"]
        own = uname
        site, portfolio, socials, chan = split_links(bio, own)
        chan = chan or rec["channel"]
        fields = {
            "tg_username": own,
            "tg_url": f"https://t.me/{own}" if own else "",
            "tg_channel": chan,
            "site": site,
            "portfolio": portfolio,
            "socials": "; ".join(socials),
            "bio": bio[:400],
        }

        target = None
        if rec["phone"]:
            target = by_phone.get(digits(rec["phone"]))
        if target is None and uname:
            target = by_handle.get(uname.lower())
        if target is None and not rec["phone"] and len(norm(rec["name"]).split()) >= 2 \
                and len(by_name.get(norm(rec["name"]), [])) == 1:
            target = by_name[norm(rec["name"])][0]

        if target is not None:
            for k, v in fields.items():
                if not v:
                    continue
                if k == "tg_username":
                    handles = [h for h in (target.get(k) or "").split("; ") if h]
                    if v not in handles:
                        handles.append(v)
                    target[k] = "; ".join(handles)
                    by_handle[v.lower()] = target
                elif not target.get(k):
                    target[k] = v
            if rec["chat"] and not target.get("tg_chat"):
                target["tg_chat"] = rec["chat"]
                stats["chat_marked_existing"] += 1
            if rec["snippet"]:
                note = (target.get("note") or "")
                if rec["snippet"][:60] not in note:
                    target["note"] = (note + " | " if note else "") + "чат: " + rec["snippet"][:180]
            accs = set(target.get("accounts") or [])
            accs.add("com.telegram.messenger")
            target["accounts"] = sorted(accs)
            stats["merged"] += 1
            continue

        newp = {
            "contact_id": f"tg:{rec['key']}",
            "name": rec["name"],
            "first": None, "last": None,
            "phones": ([{"num": rec["phone"], "type": "моб", "custom": ""}] if rec["phone"] else []),
            "emails": [], "company": None, "title": None, "department": None,
            "note": ("чат: " + rec["snippet"][:180]) if rec["snippet"] else None,
            "websites": [], "ims": [], "addresses": [],
            "nickname": None, "birthday": None, "groups": [],
            "accounts": ["com.telegram.messenger"], "starred": 0,
            "raw_ids": [], "events": [], "relations": [],
            "tg_chat": rec["chat"] or "",
            **fields,
        }
        people.append(newp)
        stats["added_from_chat" if rec["chat"] else "added_from_contacts"] += 1
        d = digits(rec["phone"])
        if d:
            by_phone[d] = newp
        n = norm(rec["name"])
        if n:
            by_name[n].append(newp)
        if uname:
            by_handle[uname.lower()] = newp

    json.dump(people, io.open(OUT, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    for k, v in sorted(stats.items()):
        print(f"  {k}: {v}")
    print("total people:", len(people))
    print("  with tg_chat:", sum(1 for p in people if p.get("tg_chat")))

if __name__ == "__main__":
    main()
