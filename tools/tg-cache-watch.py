# -*- coding: utf-8 -*-
"""Следит за кэшем Telegram и переносит новые фото в ~/Downloads/tg-cache.

Запуск:  python3 tg-cache-watch.py [минуты]
Остановка: Ctrl+C или закрыть окно.
"""
from __future__ import annotations

import hashlib
import pathlib
import shutil
import sys
import time

MEDIA = pathlib.Path.home() / (
    'Library/Group Containers/6N38VWS5BX.ru.keepcoder.Telegram/appstore/'
    'account-1317670158468557290/postbox/media'
)
DST = pathlib.Path.home() / 'Downloads' / 'tg-cache'
MIN_SIDE = 500
MIN_BYTES = 50_000


def sha256(path: pathlib.Path) -> str:
    h = hashlib.sha256()
    with path.open('rb') as f:
        for chunk in iter(lambda: f.read(1 << 20), b''):
            h.update(chunk)
    return h.hexdigest()


def is_photo(path: pathlib.Path) -> bool:
    try:
        with path.open('rb') as f:
            if f.read(3) != b'\xff\xd8\xff':
                return False
        from PIL import Image, ImageFile
        ImageFile.LOAD_TRUNCATED_IMAGES = True
        with Image.open(path) as im:
            return min(im.size) >= MIN_SIDE
    except Exception:
        return False


def run(minutes: int) -> None:
    DST.mkdir(parents=True, exist_ok=True)
    seen = {sha256(p) for p in DST.glob('*.jpg')}
    started = time.time()
    # берём только то, что появилось/обновилось после запуска (с запасом 2 минуты)
    since = started - 120
    total = 0
    print(f'слежу за кэшем {minutes} мин, папка {DST}')
    while time.time() - started < minutes * 60:
        for p in MEDIA.iterdir():
            if 'telegram-cloud-photo' not in p.name or not p.is_file():
                continue
            if p.stat().st_size < MIN_BYTES:
                continue
            if p.stat().st_mtime < since:
                continue
            digest = sha256(p)
            if digest in seen:
                continue
            if not is_photo(p):
                continue
            target = DST / f'{int(p.stat().st_mtime)}-{p.name[-24:]}.jpg'
            n = 2
            while target.exists():
                target = DST / f'{int(p.stat().st_mtime)}-{p.name[-24:]}-{n}.jpg'
                n += 1
            shutil.copy2(p, target)
            seen.add(digest)
            total += 1
            print('+', target.name)
        time.sleep(20)
    print('итого добавлено:', total)


if __name__ == '__main__':
    mins = int(sys.argv[1]) if len(sys.argv) > 1 else 45
    run(mins)
