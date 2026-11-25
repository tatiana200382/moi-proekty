#!/usr/bin/env node
// Вход в кабинет продавца Flowwow без владельца: логин и пароль берутся из Связки ключей macOS.
//
// Один раз сохранить (пароль вводится в терминале, в чат не попадает):
//   security add-generic-password -s flowwow-seller -a "<email>" -w
// Запуск:
//   node tools/flowwow-login.mjs
//
// В коде и в файлах пароль не хранится: только чтение из Keychain.

import { execFileSync } from "node:child_process";

const CDP = "http://127.0.0.1:9224";
const SERVICE = "flowwow-seller";

function keychain(flag) {
  try {
    return execFileSync("security", ["find-generic-password", "-s", SERVICE, "-w", flag].filter(Boolean), {
      encoding: "utf8",
    }).trim();
  } catch {
    return "";
  }
}

const email = keychain("-a");
const password = keychain("-w");
if (!email || !password) {
  console.log("нет данных в Связке ключей. Сохраните один раз:");
  console.log('  security add-generic-password -s flowwow-seller -a "почта" -w');
  process.exit(1);
}

const pages = await (await fetch(`${CDP}/json/list`)).json();
const tab = pages.find((t) => t.type === "page" && /flowwow\.com/.test(t.url)) || pages.find((t) => t.type === "page");
const ws = new WebSocket(tab.webSocketDebuggerUrl);
let id = 0;
const pending = new Map();
const send = (method, params = {}) =>
  new Promise((res, rej) => {
    const mid = ++id;
    pending.set(mid, { res, rej });
    ws.send(JSON.stringify({ id: mid, method, params }));
  });
await new Promise((res, rej) => {
  ws.onopen = res;
  ws.onerror = rej;
});
ws.onmessage = (ev) => {
  const m = JSON.parse(ev.data);
  if (m.id && pending.has(m.id)) {
    const { res, rej } = pending.get(m.id);
    pending.delete(m.id);
    m.error ? rej(new Error(m.error.message)) : res(m.result);
  }
};

const evaluate = async (expression) => {
  const r = await send("Runtime.evaluate", { expression, returnByValue: true });
  if (r.exceptionDetails) throw new Error(r.exceptionDetails.text);
  return r.result?.value;
};

await send("Page.enable");
await send("Page.navigate", { url: "https://flowwow.com/" });
await new Promise((r) => setTimeout(r, 6000));

// Открыть окно входа и заполнить поля
await evaluate(`(() => {
  const btn = [...document.querySelectorAll('a,button')].find(e => /Войти|Вход/.test(e.innerText || ''));
  if (btn) btn.click();
  return true;
})()`);
await new Promise((r) => setTimeout(r, 3000));

const filled = await evaluate(`(() => {
  const inputs = [...document.querySelectorAll('input')];
  const login = inputs.find(i => /email|mail|login|тел/i.test(i.type + i.name + i.placeholder));
  const pass = inputs.find(i => i.type === 'password');
  if (!login || !pass) return false;
  const set = (el, v) => {
    const s = Object.getOwnPropertyDescriptor(HTMLInputElement.prototype, 'value').set;
    s.call(el, v);
    el.dispatchEvent(new Event('input', { bubbles: true }));
  };
  set(login, ${JSON.stringify(email)});
  set(pass, ${JSON.stringify(password)});
  return true;
})()`);

if (!filled) {
  console.log("поля входа не найдены — проверьте страницу входа вручную");
  process.exit(1);
}

await evaluate(`(() => {
  const b = [...document.querySelectorAll('button')].find(e => /^Войти|Вход/.test((e.innerText || '').trim()));
  if (b) b.click();
  return true;
})()`);
await new Promise((r) => setTimeout(r, 9000));

const text = await evaluate("document.body.innerText.slice(0,600)");
const ok = /Дашборд|Товары|Заказы/.test(text || "");
console.log(ok ? "вход выполнен" : "вход не подтверждён — нужен один ручной вход");
ws.close();
process.exit(ok ? 0 : 1);
