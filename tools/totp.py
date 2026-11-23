# -*- coding: utf-8 -*-
"""Печатает текущий одноразовый код (TOTP) по секрету из ~/.config/*-totp.txt.

Использование: python3 tools/totp.py [openai]
"""
import base64
import hashlib
import hmac
import pathlib
import struct
import sys
import time

name = sys.argv[1] if len(sys.argv) > 1 else "openai"
path = pathlib.Path.home() / ".config" / f"{name}-totp.txt"
if not path.exists():
    sys.exit(f"нет файла {path}")

secret = path.read_text().strip().replace(" ", "").upper()
key = base64.b32decode(secret + "=" * ((8 - len(secret) % 8) % 8))
counter = int(time.time()) // 30
h = hmac.new(key, struct.pack(">Q", counter), hashlib.sha1).digest()
o = h[-1] & 0x0F
code = (struct.unpack(">I", h[o:o + 4])[0] & 0x7FFFFFFF) % 1000000
print(f"{code:06d}  (осталось {30 - int(time.time()) % 30} сек)")
