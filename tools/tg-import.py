# -*- coding: utf-8 -*-
"""Переносит фото из экспорта Telegram в ~/Downloads, убирает дубли, нумерует.

Использование:
    python3 tools/tg-import.py <папка_экспорта> [папка_назначения]
"""
import hashlib
import pathlib
import shutil
import sys

EXTS = {'.jpg', '.jpeg', '.png', '.heic', '.webp'}


def digest(path: pathlib.Path) -> str:
    h = hashlib.sha256()
    with path.open('rb') as f:
        for chunk in iter(lambda: f.read(1 << 20), b''):
            h.update(chunk)
    return h.hexdigest()


def main() -> int:
    if len(sys.argv) < 2:
        print('usage: tg-import.py <экспорт> [назначение]'); return 2
    src = pathlib.Path(sys.argv[1]).expanduser()
    dst = pathlib.Path(sys.argv[2]).expanduser() if len(sys.argv) > 2 else pathlib.Path.home() / 'Downloads'
    if not src.is_dir():
        print('нет папки:', src); return 2
    dst.mkdir(parents=True, exist_ok=True)

    existing = {digest(p) for p in dst.glob('*.jpg') if p.is_file()}
    photos = sorted(p for p in src.rglob('*') if p.suffix.lower() in EXTS and p.is_file())
    added = skipped = 0
    for p in photos:
        d = digest(p)
        if d in existing:
            skipped += 1
            continue
        target = dst / f'IMG_telegram_{len(existing) + 1:04d}{p.suffix.lower()}'
        shutil.copy2(p, target)
        existing.add(d)
        added += 1
    print(f'найдено фото: {len(photos)} | добавлено: {added} | дублей пропущено: {skipped}')
    print('папка:', dst)
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
