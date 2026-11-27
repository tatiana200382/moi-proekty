"""Parse Android contacts content-provider dumps into a normalized people list."""
from common import DATA, PHONE_DIR, say

import re, json, collections, sys, io, os

DUMP = str(PHONE_DIR)
OUT = str(DATA / "people.json")

ROW_RE = re.compile(r"^Row: (\d+) (.*)$")
KV_SPLIT = re.compile(r",(?=\s*[A-Za-z_][A-Za-z0-9_]*=)")

def parse_rows(path):
    rows = []
    with io.open(path, "r", encoding="utf-8", errors="replace") as f:
        for line in f:
            line = line.rstrip("\r\n")
            m = ROW_RE.match(line)
            if not m:
                continue
            body = m.group(2)
            d = {"_row": int(m.group(1))}
            for part in KV_SPLIT.split(body):
                part = part.strip()
                if "=" not in part:
                    continue
                k, v = part.split("=", 1)
                d[k.strip()] = None if v == "NULL" else v
            rows.append(d)
    return rows

PHONE_TYPES = {"0":"другой","1":"дом","2":"моб","3":"раб","4":"факс","5":"факс дом",
               "6":"факс раб","7":"пейджер","8":"другой","9":"обратный","10":"авто",
               "11":"компания","12":"ISDN","13":"осн","14":"факс","15":"радио","16":"телекс",
               "17":"TTY","18":"раб.моб","19":"раб.пейджер","20":"ассистент"}
EMAIL_TYPES = {"0":"другой","1":"дом","2":"раб","3":"другой","4":"моб"}
ADDR_TYPES = {"0":"другой","1":"дом","2":"раб","3":"другой"}

def main():
    contacts = parse_rows(os.path.join(DUMP, "contacts.txt"))
    data = parse_rows(os.path.join(DUMP, "data2.txt"))
    raws = parse_rows(os.path.join(DUMP, "raw_contacts.txt"))
    groups = parse_rows(os.path.join(DUMP, "groups.txt"))

    gtitle = {g["_id"]: g.get("title") or "" for g in groups}
    raw_acct = {r["_id"]: (r.get("account_type") or "", r.get("account_name") or "")
                for r in raws}

    people = collections.OrderedDict()
    def person(cid):
        if cid not in people:
            people[cid] = {
                "contact_id": cid, "name": None, "first": None, "last": None,
                "phones": [], "emails": [], "company": None, "title": None,
                "department": None, "note": None, "websites": [], "ims": [],
                "addresses": [], "nickname": None, "birthday": None,
                "groups": set(), "accounts": set(), "starred": 0,
                "raw_ids": set(), "events": [], "relations": [],
            }
        return people[cid]

    for c in contacts:
        p = person(c["_id"])
        p["name"] = (c.get("display_name") or "").strip() or None
        p["starred"] = int(c.get("starred") or 0)

    for d in data:
        cid = d.get("contact_id")
        if not cid:
            continue
        p = person(cid)
        mt = (d.get("mimetype") or "").rsplit("/", 1)[-1]
        if d.get("raw_contact_id"):
            p["raw_ids"].add(d["raw_contact_id"])
        v1, v2 = d.get("data1"), d.get("data2")

        if mt == "name":
            full = (v1 or "").strip()
            p["first"] = (d.get("data2") or "").strip() or p["first"]
            p["last"] = (d.get("data3") or "").strip() or p["last"]
            if full and (not p["name"] or len(full) > len(p["name"])):
                p["name"] = full
        elif mt == "phone_v2":
            if v1:
                p["phones"].append({"num": v1.strip(),
                                    "type": PHONE_TYPES.get(v2 or "0", "другой"),
                                    "custom": (d.get("data3") or "").strip()})
        elif mt == "email_v2":
            if v1:
                p["emails"].append({"email": v1.strip().lower(),
                                    "type": EMAIL_TYPES.get(v2 or "0", "другой")})
        elif mt == "organization":
            p["company"] = (v1 or "").strip() or p["company"]
            p["title"] = (d.get("data4") or "").strip() or p["title"]
            p["department"] = (d.get("data5") or "").strip() or p["department"]
        elif mt == "note":
            if v1 and v1.strip():
                p["note"] = (p["note"] + " | " + v1.strip()) if p["note"] else v1.strip()
        elif mt == "website":
            if v1: p["websites"].append(v1.strip())
        elif mt == "im":
            if v1: p["ims"].append({"handle": v1.strip(), "proto": (d.get("data5") or "").strip()})
        elif mt == "postal":
            parts = [ (d.get(f"data{i}") or "").strip() for i in range(4, 10) ]
            parts = [x for x in parts if x]
            if parts or v1:
                p["addresses"].append({"type": ADDR_TYPES.get(v2 or "0","другой"),
                                       "text": ", ".join(parts) or (v1 or "")})
        elif mt == "nickname":
            if v1: p["nickname"] = v1.strip()
        elif mt == "birthday":
            if v1: p["birthday"] = v1.strip()
        elif mt == "group_membership":
            if v1 and v1 in gtitle:
                p["groups"].add(gtitle[v1])
        elif mt == "contact_event":
            if v1: p["events"].append(v1.strip())
        elif mt == "relation":
            if v1: p["relations"].append(v1.strip())

    for cid, p in people.items():
        for rid in p["raw_ids"]:
            if rid in raw_acct:
                p["accounts"].add(raw_acct[rid][0])
        p["groups"] = sorted(p["groups"])
        p["accounts"] = sorted(p["accounts"])
        p["raw_ids"] = sorted(p["raw_ids"])

    out = list(people.values())
    # keep only contacts with some identifying signal
    out = [p for p in out if (p["name"] or p["phones"] or p["emails"] or p["company"])]

    with io.open(OUT, "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=1)

    n = len(out)
    with_phone = sum(1 for p in out if p["phones"])
    with_email = sum(1 for p in out if p["emails"])
    with_company = sum(1 for p in out if p["company"])
    with_note = sum(1 for p in out if p["note"])
    print(f"contacts total: {n}")
    print(f"  with phone:   {with_phone}")
    print(f"  with email:   {with_email}")
    print(f"  with company: {with_company}")
    print(f"  with note:    {with_note}")
    print("accounts:", collections.Counter(a for p in out for a in p["accounts"]).most_common(12))
    print("groups:", collections.Counter(g for p in out for g in p["groups"]).most_common(15))

if __name__ == "__main__":
    main()
