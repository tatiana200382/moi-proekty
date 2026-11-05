"""Переименование товара в прайс-листе Яндекс.Бизнеса через управляемый браузер.

Использование: python3 fixname.py "старое название" "новое название"
Работает только если браузер запущен с отладочным портом 9222 (см. cdp.mjs).
"""
import json
import subprocess
import sys
import time

NODE = "/usr/local/bin/node"
HERE = "/Users/tatiana/Desktop/Обучение ИИ/Мои проекты/ii-marketolog/tools"


def run_js(js: str, timeout=25):
    path = f"{HERE}/js/_tmp.js"
    with open(path, "w", encoding="utf-8") as f:
        f.write(js)
    out = subprocess.run(
        [NODE, "cdp.mjs", "evalfile", "js/_tmp.js", "0"],
        capture_output=True, text=True, cwd=HERE, timeout=timeout,
    )
    return (out.stdout or out.stderr or "").strip()


CLOSE_MODAL = """
(() => {
  const b = [...document.querySelectorAll('button')].find(x => x.innerText.trim() === 'Отменить');
  if (b && document.body.innerText.includes('Редактировать товар')) { b.click(); return 'закрыл форму'; }
  return 'формы нет';
})()
"""


def open_item(old: str) -> str:
    js = f"""
(() => {{
  const t = {json.dumps(old, ensure_ascii=False)};
  const el = [...document.querySelectorAll('*')].find(x => x.children.length === 0 && x.textContent.trim() === t);
  if (!el) return 'НЕ НАЙДЕНО';
  el.scrollIntoView({{ block: 'center' }});
  el.click();
  return 'открыт';
}})()
"""
    return run_js(js)


def set_name(old: str, new: str) -> str:
    js = f"""
(() => {{
  const oldName = {json.dumps(old, ensure_ascii=False)};
  const newName = {json.dumps(new, ensure_ascii=False)};
  const input = [...document.querySelectorAll('input')].find(i => i.value.trim() === oldName);
  if (!input) return 'ПОЛЕ НЕ НАЙДЕНО';
  const setter = Object.getOwnPropertyDescriptor(HTMLInputElement.prototype, 'value').set;
  setter.call(input, newName);
  input.dispatchEvent(new Event('input', {{ bubbles: true }}));
  input.dispatchEvent(new Event('change', {{ bubbles: true }}));
  const btn = [...document.querySelectorAll('button')].find(b => b.innerText.trim() === 'Внести изменения');
  if (!btn) return 'КНОПКА НЕ НАЙДЕНА';
  btn.click();
  return 'СОХРАНЕНО';
}})()
"""
    return run_js(js)


def main():
    if len(sys.argv) < 3:
        print("нужны два аргумента: старое и новое название")
        return 1
    old, new = sys.argv[1], sys.argv[2]
    run_js(CLOSE_MODAL)
    time.sleep(0.6)
    opened = open_item(old)
    if "НЕ НАЙДЕНО" in opened:
        print(f"{old} :: не найдено на странице")
        return 1
    time.sleep(1.6)
    saved = set_name(old, new)
    time.sleep(3.5)
    print(f"{old} → {new} :: {saved}")
    return 0 if "СОХРАНЕНО" in saved else 1


if __name__ == "__main__":
    sys.exit(main())
