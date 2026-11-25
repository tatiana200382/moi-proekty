#!/usr/bin/env python3
"""Локальный HTTP-прокси, который пересылает запросы через наш SOCKS-туннель (127.0.0.1:1082).
Нужен для программ, которые не понимают socks5 в переменных окружения (например, codex-cli)."""
import asyncio, struct

LISTEN_HOST, LISTEN_PORT = "127.0.0.1", 8118
SOCKS_HOST, SOCKS_PORT = "127.0.0.1", 1082


async def socks5_connect(host: str, port: int):
    r, w = await asyncio.open_connection(SOCKS_HOST, SOCKS_PORT)
    w.write(b"\x05\x01\x00")
    await w.drain()
    if await r.readexactly(2) != b"\x05\x00":
        raise ConnectionError("socks: handshake failed")
    hb = host.encode()
    w.write(b"\x05\x01\x00\x03" + bytes([len(hb)]) + hb + struct.pack("!H", port))
    await w.drain()
    rep = await r.readexactly(4)
    if rep[1] != 0:
        raise ConnectionError(f"socks: connect failed {rep[1]}")
    atyp = rep[3]
    if atyp == 1:
        await r.readexactly(4)
    elif atyp == 3:
        ln = (await r.readexactly(1))[0]
        await r.readexactly(ln)
    elif atyp == 4:
        await r.readexactly(16)
    await r.readexactly(2)
    return r, w


async def pipe(reader, writer):
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


async def handle(reader, writer):
    try:
        line = await reader.readline()
        if not line:
            writer.close(); return
        method, target, _ = line.decode(errors="ignore").split()
        headers = []
        while True:
            h = await reader.readline()
            if h in (b"\r\n", b"\n", b""):
                break
            headers.append(h)
        if method.upper() != "CONNECT":
            writer.write(b"HTTP/1.1 405 Method Not Allowed\r\n\r\n")
            await writer.drain(); writer.close(); return
        host, _, port = target.rpartition(":")
        up_r, up_w = await socks5_connect(host, int(port or 443))
        writer.write(b"HTTP/1.1 200 Connection Established\r\n\r\n")
        await writer.drain()
        await asyncio.gather(pipe(reader, up_w), pipe(up_r, writer))
    except Exception:
        try:
            writer.close()
        except Exception:
            pass


async def main():
    server = await asyncio.start_server(handle, LISTEN_HOST, LISTEN_PORT)
    print(f"HTTP-прокси слушает {LISTEN_HOST}:{LISTEN_PORT} → SOCKS {SOCKS_HOST}:{SOCKS_PORT}", flush=True)
    async with server:
        await server.serve_forever()


if __name__ == "__main__":
    asyncio.run(main())
