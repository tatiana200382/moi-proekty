#!/usr/bin/env node
// Управление Chrome на порту 9224 для сбора заявок.
//
//   node browser.mjs run <script.js> <url> [css-селектор ожидания]
//   node browser.mjs eval "<выражение>" <часть-url>
//   node browser.mjs shot <out.png> <часть-url>
//   node browser.mjs list
//
// run открывает (или переиспользует) отдельную вкладку, перезагружает страницу,
// ждёт селектор и выполняет скрипт из файла. На stdout — только JSON.
// Никаких кликов и отправок: только навигация и чтение.

import fs from "node:fs/promises";
import path from "node:path";

const PORT = process.env.CDP_PORT || 9224;
const BASE = `http://127.0.0.1:${PORT}`;
const cmd = process.argv[2];
const args = process.argv.slice(3);

const sleep = (ms) => new Promise((r) => setTimeout(r, ms));

async function listPages() {
  const res = await fetch(`${BASE}/json/list`);
  if (!res.ok) throw new Error(`CDP ${res.status}: Chrome не отвечает на ${PORT}`);
  return (await res.json()).filter((t) => t.type === "page");
}

async function openTab(url) {
  const res = await fetch(`${BASE}/json/new?${encodeURIComponent(url)}`, { method: "PUT" });
  if (!res.ok) throw new Error(`не удалось открыть вкладку: ${res.status}`);
  return res.json();
}

async function findPage(needle) {
  const pages = await listPages();
  return pages.find((p) => p.url.includes(needle)) || null;
}

async function ensurePage(url, needle) {
  let page = await findPage(needle);
  if (!page) {
    await openTab(url);
    for (let i = 0; i < 20; i++) {
      await sleep(500);
      page = await findPage(needle);
      if (page) break;
    }
  }
  if (!page) throw new Error(`вкладка не открылась: ${url}`);
  return page;
}

async function connect(wsUrl) {
  const ws = new WebSocket(wsUrl);
  await new Promise((resolve, reject) => {
    ws.addEventListener("open", resolve, { once: true });
    ws.addEventListener("error", () => reject(new Error("не удалось подключиться к вкладке")), { once: true });
  });
  let seq = 0;
  const pending = new Map();
  ws.addEventListener("message", (ev) => {
    const msg = JSON.parse(ev.data);
    if (msg.id && pending.has(msg.id)) {
      const { resolve, reject, timer } = pending.get(msg.id);
      pending.delete(msg.id);
      clearTimeout(timer);
      if (msg.error) reject(new Error(msg.error.message || JSON.stringify(msg.error)));
      else resolve(msg.result);
    }
  });
  const send = (method, params = {}, timeout = 30000) =>
    new Promise((resolve, reject) => {
      const id = ++seq;
      const timer = setTimeout(() => {
        pending.delete(id);
        reject(new Error(`таймаут ${method}`));
      }, timeout);
      pending.set(id, { resolve, reject, timer });
      ws.send(JSON.stringify({ id, method, params }));
    });
  return { ws, send };
}

async function evaluate(send, expression) {
  const r = await send("Runtime.evaluate", {
    expression,
    returnByValue: true,
    awaitPromise: true,
    userGesture: false,
  });
  if (r.exceptionDetails) {
    const d = r.exceptionDetails;
    throw new Error(d.exception?.description || d.text || "ошибка в скрипте страницы");
  }
  return r.result?.value;
}

async function waitReady(send, selector) {
  // Ждём загрузку и появление селектора, но не дольше 25 секунд.
  for (let i = 0; i < 50; i++) {
    try {
      const state = await evaluate(
        send,
        `JSON.stringify({ready: document.readyState, found: ${selector ? `!!document.querySelector(${JSON.stringify(selector)})` : "true"}})`
      );
      const s = JSON.parse(state);
      if (s.ready === "complete" && s.found) return true;
    } catch {
      // во время навигации контекст может исчезать — это нормально
    }
    await sleep(500);
  }
  return false;
}

async function run() {
  const [scriptFile, url, selector] = args;
  if (!scriptFile || !url) throw new Error("нужно: run <script.js> <url> [селектор]");
  const page = await ensurePage(url, url.replace(/^https?:\/\/[^/]+/, ""));
  const { ws, send } = await connect(page.webSocketDebuggerUrl);
  try {
    await send("Page.enable");
    await send("Page.navigate", { url });
    await sleep(1200);
    const ready = await waitReady(send, selector);
    if (!ready) console.error(`предупреждение: страница не дождалась ${selector || "загрузки"}`);
    const src = await fs.readFile(path.resolve(scriptFile), "utf-8");
    const value = await evaluate(send, src);
    console.log(JSON.stringify(value ?? null));
  } finally {
    ws.close();
  }
}

async function evalOnPage() {
  const [expression, needle] = args;
  if (!expression || !needle) throw new Error("нужно: eval <выражение> <часть-url>");
  const page = await findPage(needle);
  if (!page) throw new Error(`нет вкладки с адресом: ${needle}`);
  const { ws, send } = await connect(page.webSocketDebuggerUrl);
  try {
    const value = await evaluate(send, expression);
    console.log(JSON.stringify(value ?? null));
  } finally {
    ws.close();
  }
}

async function screenshot() {
  const [out, needle] = args;
  if (!out || !needle) throw new Error("нужно: shot <out.png> <часть-url>");
  const page = await findPage(needle);
  if (!page) throw new Error(`нет вкладки с адресом: ${needle}`);
  const { ws, send } = await connect(page.webSocketDebuggerUrl);
  try {
    await send("Page.enable");
    const shot = await send("Page.captureScreenshot", { format: "png" });
    await fs.writeFile(out, Buffer.from(shot.data, "base64"));
    console.log(out);
  } finally {
    ws.close();
  }
}

(async () => {
  if (cmd === "list") {
    for (const p of await listPages()) console.log(`${p.title.slice(0, 45)}\t${p.url.slice(0, 90)}`);
  } else if (cmd === "run") {
    await run();
  } else if (cmd === "eval") {
    await evalOnPage();
  } else if (cmd === "shot") {
    await screenshot();
  } else {
    console.error("команды: run | eval | shot | list");
    process.exit(2);
  }
  process.exit(0);
})().catch((e) => {
  console.error(`ошибка: ${e.message}`);
  process.exit(1);
});
