#!/usr/bin/env node
// Держит сессию продавца Flowwow живой без участия владельца.
// Что делает: проверяет кабинет; если открыт — обновляет сохранённые куки;
// если закрыт — восстанавливает куки из ~/.config/flowwow/cookies.json и проверяет снова.
// Запуск: node tools/flowwow-keepalive.mjs   (по расписанию — раз в 6 часов)

import fs from "node:fs";
import os from "node:os";
import path from "node:path";
import { execFileSync } from "node:child_process";

const DIR = path.join(os.homedir(), ".config", "flowwow");
const FILE = path.join(DIR, "cookies.json");
const LOG = path.join(DIR, "keepalive.log");
const ADMIN = "https://flowwow.com/admin/dashboard";
const CDP = "http://127.0.0.1:9224";

const log = (msg) => {
  const line = `${new Date().toISOString()} ${msg}\n`;
  fs.mkdirSync(DIR, { recursive: true, mode: 0o700 });
  fs.appendFileSync(LOG, line);
  console.log(msg.trim());
};

async function pages() {
  const r = await fetch(`${CDP}/json/list`);
  return (await r.json()).filter((t) => t.type === "page");
}

async function ensureTab() {
  const list = await pages();
  let tab = list.find((t) => /flowwow\.com\/admin/.test(t.url)) || list.find((t) => /flowwow\.com/.test(t.url));
  if (tab) return tab;
  const r = await fetch(`${CDP}/json/new?${encodeURIComponent(ADMIN)}`, { method: "PUT" });
  tab = await r.json();
  await new Promise((res) => setTimeout(res, 4000));
  return (await pages()).find((t) => t.id === tab.id) || tab;
}

async function evaluate(tab, expression) {
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
  try {
    const r = await send("Runtime.evaluate", { expression, returnByValue: true, awaitPromise: true });
    return r.result?.value;
  } finally {
    ws.close();
  }
}

async function isOpen(tab) {
  const text = await evaluate(tab, "document.body.innerText.slice(0,800)");
  return typeof text === "string" && /Дашборд|Товары|Заказы/.test(text) && !/Укажите адрес доставки/.test(text);
}

async function main() {
  if (!fs.existsSync(FILE)) {
    log("нет сохранённых куки — нужен один вход владельца и save");
    process.exit(1);
  }
  let tab = await ensureTab();
  if (await isOpen(tab)) {
    execFileSync(process.execPath, [path.join(import.meta.dirname, "flowwow-auth.mjs"), "save"], { stdio: "ignore" });
    log("сессия открыта, куки обновлены");
    return;
  }
  log("сессия закрыта — восстанавливаю куки");
  execFileSync(process.execPath, [path.join(import.meta.dirname, "flowwow-auth.mjs"), "restore"], { stdio: "ignore" });
  await new Promise((res) => setTimeout(res, 7000));
  tab = await ensureTab();
  if (await isOpen(tab)) {
    execFileSync(process.execPath, [path.join(import.meta.dirname, "flowwow-auth.mjs"), "save"], { stdio: "ignore" });
    log("сессия восстановлена, куки обновлены");
  } else {
    log("восстановить не удалось — нужен вход владельца (сессия на сервере истекла)");
    process.exit(1);
  }
}

const hardStop = setTimeout(() => {
  log("принудительный выход по таймауту 120 с");
  process.exit(2);
}, 120000);

main()
  .then(() => {
    clearTimeout(hardStop);
    process.exit(0);
  })
  .catch((e) => {
    log("ошибка: " + e.message);
    process.exit(1);
  });
