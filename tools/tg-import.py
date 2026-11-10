# -*- coding: utf-8 -*-
"""Переносит фото из экспорта Telegram в папку назначения (по умолчанию ~/Downloads).

- Собирает только изображения из указанной папки (без подпапок, если не указан --recursive).
- Пропускает дубли по SHA-256 среди уже лежащих там изображений.
- Не перезаписывает существующие файлы: при совпадении имени добавляет суффикс.

Использование:
    python3 tg-import.py <папка_экспорта> [папка_назначения] [--recursive] [--dry-run]
"""
from __future__ import annotations

import argparse
import hashlib
import pathlib
import shutil

EXTS = {'.jpg', '.jpeg', '.png', '.heic', '.webp', '.gif'}


def sha256(path: pathlib.Path) -> str:
    h = hashlib.sha256()
    with path.open('rb') as f:
        for chunk in iter(lambda: f.read(1 << 20), b''):
            h.update(chunk)
    return h.hexdigest()


def images_in(folder: pathlib.Path, recursive: bool) -> list[pathlib.Path]:
    it = folder.rglob('*') if recursive else folder.glob('*')
    return sorted(p for p in it if p.is_file() and p.suffix.lower() in EXTS)


def free_name(dst: pathlib.Path, name: str) -> pathlib.Path:
    target = dst / name
    if not target.exists():
        return target
    stem, suffix = target.stem, target.suffix
    i = 2
    while True:
        candidate = dst / f'{stem}_{i}{suffix}'
        if not candidate.exists():
            return candidate
        i += 1


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument('source')
    ap.add_argument('destination', nargs='?', default=str(pathlib.Path.home() / 'Downloads'))
    ap.add_argument('--recursive', action='store_true')
    ap.add_argument('--dry-run', action='store_true')
    args = ap.parse_args()

    src = pathlib.Path(args.source).expanduser()
    dst = pathlib.Path(args.destination).expanduser()
    if not src.is_dir():
        print('нет папки экспорта:', src)
        return 2
    dst.mkdir(parents=True, exist_ok=True)

    existing = {sha256(p) for p in images_in(dst, recursive=False)}
    photos = images_in(src, recursive=args.recursive)
    added = skipped = 0
    planned = []
    for p in photos:
        digest = sha256(p)
        if digest in existing:
            skipped += 1
            continue
        target = free_name(dst, f'tg_{p.name}')
        planned.append((p, target))
        existing.add(digest)
        added += 1

    if args.dry_run:
        print(f'[dry-run] к добавлению: {added}, дублей: {skipped}')
        for _, t in planned[:10]:
            print('  ->', t.name)
        return 0

    for p, target in planned:
        shutil.copy2(p, target)
    print(f'найдено: {len(photos)} | добавлено: {added} | дублей пропущено: {skipped}')
    print('папка:', dst)
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
