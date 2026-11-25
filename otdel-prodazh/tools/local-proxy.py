# -*- coding: utf-8 -*-
"""Локальный прокси без пароля: пересылает запросы в немецкий прокси с авторизацией.

Слушает 127.0.0.1:8118, добавляет заголовок Proxy-Authorization и передаёт дальше.
Нужен потому, что Chrome на macOS не умеет прокси с логином в адресе.

    python3 local-proxy.py            # запустить
"""
from __future__ import annotations

import asyncio
import base64
import os

UPSTREAM_HOST = "2.31.104.44"
UPSTREAM_PORT = 3128
USER = "silver"
PASS = "BMKMODAVR8k7XTD2"
LISTEN_HOST = "127.0.0.1"
LISTEN_PORT = 8118

AUTH = base64.b64encode(f"{USER}:{PASS}".encode()).decode()


async def pipe(reader: asyncio.StreamReader, writer: asyncio.StreamWriter) -> None:
    try:
        while data := await reader.read(65536):
            writer.write(data)
            await writer.drain()
    except Exception:
        pass
    finally:
        try:
            writer.close()
        except Exception:
            pass


async def handle(client_reader: asyncio.StreamReader, client_writer: asyncio.StreamWriter) -> None:
    try:
        head = await client_reader.readuntil(b"\r\n\r\n")
    except Exception:
        client_writer.close()
        return

    text = head.decode("latin-1")
    first, *rest = text.split("\r\n")
    parts = first.split()
    if len(parts) < 2:
        client_writer.close()
        return

    method, target = parts[0], parts[1]
    headers = [h for h in rest if h and not h.lower().startswith("proxy-authorization")]
    headers.append(f"Proxy-Authorization: Basic {AUTH}")

    # Подключаемся к немецкому прокси; если он недоступен — идём напрямую (страховка)
    use_upstream = True
    try:
        up_reader, up_writer = await asyncio.open_connection(UPSTREAM_HOST, UPSTREAM_PORT)
    except Exception:
        use_upstream = False
        host, _, port = target.partition(":")
        try:
            up_reader, up_writer = await asyncio.open_connection(host, int(port or 443))
        except Exception:
            client_writer.close()
            return
        if method.upper() == "CONNECT":
            client_writer.write(b"HTTP/1.1 200 Connection Established\r\n\r\n")
            await client_writer.drain()
            await asyncio.gather(pipe(client_reader, up_writer), pipe(up_reader, client_writer))
            return

    if not use_upstream:
        req = f"{method} {target} HTTP/1.1\r\n" + "\r\n".join(
            [h for h in headers if not h.lower().startswith("proxy-authorization")]) + "\r\n\r\n"
    elif method.upper() == "CONNECT":
        req = f"CONNECT {target} HTTP/1.1\r\n" + "\r\n".join(headers) + "\r\n\r\n"
    else:
        req = f"{method} {target} HTTP/1.1\r\n" + "\r\n".join(headers) + "\r\n\r\n"

    up_writer.write(req.encode("latin-1"))
    await up_writer.drain()

    # Ответ на CONNECT или на обычный запрос — отдаём клиенту
    try:
        resp = await up_reader.readuntil(b"\r\n\r\n")
    except Exception:
        client_writer.close(); up_writer.close(); return
    client_writer.write(resp)
    await client_writer.drain()

    if method.upper() == "CONNECT" and b"200" in resp.split(b"\r\n")[0]:
        # туннель: перекачиваем в обе стороны
        await asyncio.gather(pipe(client_reader, up_writer), pipe(up_reader, client_writer))
    else:
        client_writer.close()
        up_writer.close()


async def main() -> None:
    server = await asyncio.start_server(handle, LISTEN_HOST, LISTEN_PORT)
    print(f"локальный прокси на {LISTEN_HOST}:{LISTEN_PORT} → {UPSTREAM_HOST}:{UPSTREAM_PORT}")
    async with server:
        await server.serve_forever()


if __name__ == "__main__":
    asyncio.run(main())
