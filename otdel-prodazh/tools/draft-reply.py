# -*- coding: utf-8 -*-
"""Черновик ответа клиенту через наш сервер Ollama.

    python3 otdel-prodazh/tools/draft-reply.py "Сколько стоит букет из 15 роз?"
    python3 otdel-prodazh/tools/draft-reply.py --model qwen3.8:27b "..."

Сервер по умолчанию: http://ai.m-tik.com:11434 (переопределяется OLLAMA_URL).
"""
from __future__ import annotations

import json
import os
import sys
import time
import urllib.request

URL = os.environ.get("OLLAMA_URL", "http://ai.m-tik.com:11434")
MODEL = os.environ.get("OLLAMA_MODEL", "llama3.1:8b")

SYSTEM = (
    "Ты флорист цветочного магазина Silver Song Flowers в Санкт-Петербурге. "
    "Три магазина: Ленинский пр. 56, ул. Трибуца 8, ул. Белышева 5/6. Доставка от 500 ₽. "
    "Пиши по-русски, коротко (2–4 предложения), вежливо, без выдуманных цен и сроков. "
    "Если нужна цена — скажи, что флорист уточнит состав и подтвердит стоимость. "
    "Уточняй дату, цветы и адрес доставки одним вопросом."
)


def ask(prompt: str, model: str = MODEL, timeout: int = 180) -> tuple[str, float, int]:
    body = json.dumps({
        "model": model,
        "stream": False,
        "messages": [
            {"role": "system", "content": SYSTEM},
            {"role": "user", "content": prompt},
        ],
        "options": {"temperature": 0.4, "num_predict": 220},
    }).encode()
    req = urllib.request.Request(f"{URL}/api/chat", data=body,
                                 headers={"Content-Type": "application/json"})
    t0 = time.time()
    with urllib.request.urlopen(req, timeout=timeout) as r:
        data = json.load(r)
    return data.get("message", {}).get("content", "").strip(), time.time() - t0, data.get("eval_count", 0)


def main() -> int:
    args = sys.argv[1:]
    if not args:
        print(__doc__)
        return 1
    model = MODEL
    if args[0] == "--model":
        model = args[1]
        args = args[2:]
    text = " ".join(args)
    answer, secs, tokens = ask(text, model)
    print(answer)
    print(f"\n— {model}, {secs:.1f} с, {tokens} токенов")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
