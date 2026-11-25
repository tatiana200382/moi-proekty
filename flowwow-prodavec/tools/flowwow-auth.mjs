#!/usr/bin/env node
// Сохранение и восстановление сессии продавца Flowwow для управляемого Chrome (CDP 9224).
// Куки хранятся ВНЕ проекта: ~/.config/flowwow/cookies.json (права 600). В чат и в git не попадают.
//
//   node flowwow-auth.mjs save      — сохранить куки flowwow из текущего Chrome
//   node flowwow-auth.mjs restore   — вернуть куки в Chrome (после закрытия браузера)
//   node flowwow-auth.mjs check     — проверить, авторизован ли кабинет продавца

import fs from "node:fs";
import os from "node:os";
import path from "node:path";

const CDP = process.env.CDP_URL || "http://127.0.0.1:9224";
const DIR = path.join(os.homedir(), ".config", "flowwow");
const FILE = path.join(DIR, "cookies.json");
const CHECK_URL = "https://flowwow.com/admin/profile/shop/";

async function targets() {
  const r = await fetch(`${CDP}/json/list`);
  return (await r.json()).filter((t) => t.type === "page");
}

async function withTab(fn) {
  let list = await targets();
  let tab = list.find((t) => t.url.includes("flowwow.com/admin")) || list.find((t) => t.url.includes("flowwow.com"));
  if (!tab) {
    const r = await fetch(`${CDP}/json/new?about:blank`, { method: "PUT" });
    tab = await r.json();
    await new Promise((res) => setTimeout(res, 1200));
    list = await targets();
    tab = list.find((t) => t.id === tab.id) || tab;
  }
  if (!tab) throw new Error("нет вкладок в Chrome");
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
    const msg = JSON.parse(ev.data);
    if (msg.id && pending.has(msg.id)) {
      const { res, rej } = pending.get(msg.id);
      pending.delete(msg.id);
      msg.error ? rej(new Error(msg.error.message)) : res(msg.result);
    }
  };
  try {
    return await fn(send, tab);
  } finally {
    ws.close();
  }
}

const isFlowwow = (c) => /(^|\.)flowwow\.com$/.test(c.domain.replace(/^\./, ""));

async function save() {
  const cookies = await withTab(async (send) => {
    await send("Network.enable");
    const r = await send("Network.getAllCookies");
    return r.cookies.filter(isFlowwow);
  });
  if (!cookies.length) {
    console.log("куки flowwow не найдены — вероятно, вход не выполнен");
    process.exit(1);
  }
  fs.mkdirSync(DIR, { recursive: true, mode: 0o700 });
  fs.writeFileSync(FILE, JSON.stringify(cookies, null, 1), { mode: 0o600 });
  const names = [...new Set(cookies.map((c) => c.name))].sort();
  console.log(`сохранено ${cookies.length} куки в ${FILE}`);
  console.log("имена:", names.join(", "));
}

async function restore() {
  if (!fs.existsSync(FILE)) {
    console.log("файла нет:", FILE);
    process.exit(1);
  }
  const cookies = JSON.parse(fs.readFileSync(FILE, "utf8"));
  await withTab(async (send, tab) => {
    await send("Network.enable");
    await send("Network.setCookies", {
      cookies: cookies.map((c) => ({
        name: c.name,
        value: c.value,
        domain: c.domain,
        path: c.path || "/",
        secure: c.secure,
        httpOnly: c.httpOnly,
        sameSite: c.sameSite,
        expires: c.expires,
      })),
    });
    await send("Page.enable");
    await send("Page.navigate", { url: CHECK_URL });
  });
  console.log(`восстановлено ${cookies.length} куки, открыт кабинет`);
}

async function check() {
  const tab = (await targets()).find((t) => t.url.includes("flowwow.com"));
  if (!tab) {
    console.log("вкладки flowwow нет — открой https://flowwow.com/admin/profile/shop/");
    process.exit(1);
  }
  const text = await withTab(async (send) => {
    const r = await send("Runtime.evaluate", {
      expression: "document.body.innerText.slice(0, 600)",
      returnByValue: true,
    });
    return r.result?.value || "";
  });
  const inside = /Моя витрина|Дашборд|Товары/.test(text) && !/Укажите адрес доставки/.test(text);
  console.log(inside ? "кабинет продавца ОТКРЫТ" : "кабинет ЗАКРЫТ — нужен вход или restore");
  console.log("вкладка:", tab.url);
}

async function open() {
  if (fs.existsSync(FILE)) {
    await restore();
  } else {
    console.log("куки не сохранены — выполни save, пока кабинет открыт");
  }
  await new Promise((res) => setTimeout(res, 12000));
  await check();
  if (!fs.existsSync(FILE)) return;
  lines: {
    const tab = (await targets()).find((t) => t.url.includes("flowwow.com"));
    if (!tab) break lines;
    const text = await withTab(async (send) => {
      const r = await send("Runtime.evaluate", {
        expression: "document.body.innerText.slice(0,800)",
        returnByValue: true,
      });
      return r.result?.value || "";
    });
    if (!/Моя витрина|Дашборд|Товары/.test(text)) {
      console.log("страница ещё загружается — проверьте через несколько секунд: node tools/flowwow-auth.mjs check");
    }
  }
}

const cmd = process.argv[2];
const run = { save, restore, check, open }[cmd];
if (!run) {
  console.log("команды: save | restore | check | open");
  process.exit(2);
}
run().catch((e) => {
  console.error("ошибка:", e.message);
  process.exit(1);
});
