"""Проверка доступа к кабинету Яндекс.Бизнеса.

Читает куки из ~/.config/yandex-business/cookies.env и показывает только наличие и длину
значений — сами секреты не печатает. Ничего не меняет в карточке.
"""
import os
import sys

COOKIES = os.path.expanduser("~/.config/yandex-business/cookies.env")


def load():
    if not os.path.exists(COOKIES):
        print(f"Файл не найден: {COOKIES}")
        return {}
    pairs = {}
    with open(COOKIES, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, _, value = line.partition("=")
            pairs[key.strip()] = value.strip()
    return pairs


def main():
    pairs = load()
    ok = True
    for key in ("SESSION_ID", "SESSION_ID2"):
        value = pairs.get(key, "")
        state = "заполнено" if len(value) > 20 else "пусто"
        print(f"{key}: {state}" + (f" ({len(value)} символов)" if value else ""))
        if len(value) <= 20:
            ok = False
    if not ok:
        print("\nНужно вставить оба значения в", COOKIES)
        return 1
    print("\nКуки на месте. Можно делать проверку чтением — без изменений в карточке.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
