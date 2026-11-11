#!/usr/bin/env node
/**
 * browser.mjs — управление Chrome под управлением (CDP, порт 9224).
 *
 * Команды:
 *   node browser.mjs tabs
 *   node browser.mjs open <url> [--wait 6000]
 *   node browser.mjs text <url|-> [--wait 6000] [--out файл]
 *   node browser.mjs login-status
 *   node browser.mjs shot <out.png> [--url <url>] [--wait 6000]
 *   node browser.mjs eval "<js>"
 *   node browser.mjs new <url>
 *   node browser.mjs close <index>
 *
 * Переменные: CDP_PORT (по умолчанию 9224).
 */
import fs from "node:fs/promises";

const PORT = process.env.CDP_PORT || 9224;
const BASE = `http://127.0.0.1:${PORT}`;
const args = process.argv.slice(2);
const cmd = args[0] || "tabs";

const sleep = (ms) => new Promise((r) => setTimeout(r, ms));

async function pages() {
  const res = await fetch(`${BASE}/json/list`);
  const list = await res.json();
  return list.filter((t) => t.type === "page");
}

async function connect(url) {
  const ws = new WebSocket(url);
  await new Promise((res, rej) => {
    ws.addEventListener("open", res, { once: true });
    ws.addEventListener("error", rej, { once: true });
  });
  let id = 0;
  const pending = new Map();
  ws.addEventListener("message", (ev) => {
    const m = JSON.parse(ev.data);
    if (m.id && pending.has(m.id)) {
      const p = pending.get(m.id);
      pending.delete(m.id);
      m.error ? p.reject(new Error(JSON.stringify(m.error))) : p.resolve(m.result);
    }
  });
  const send = (method, params = {}) =>
    new Promise((resolve, reject) => {
      const i = ++id;
      pending.set(i, { resolve, reject });
      ws.send(JSON.stringify({ id: i, method, params }));
      setTimeout(() => {
        if (pending.has(i)) {
          pending.delete(i);
          reject(new Error(`таймаут ${method}`));
        }
      }, 45000);
    });
  return { ws, send };
}

function flag(name, def) {
  const i = args.indexOf(`--${name}`);
  return i === -1 ? def : args[i + 1];
}

async function withPage(fn, tabIndex = 0) {
  const list = await pages();
  const page = list[tabIndex];
  if (!page) throw new Error("нет вкладок — Chrome под управлением не запущен?");
  const { ws, send } = await connect(page.webSocketDebuggerUrl);
  try {
    await send("Page.enable");
    await send("Runtime.enable");
    return await fn(send);
  } finally {
    ws.close();
  }
}

const CABINETS = [
  { name: "Яндекс.Бизнес", url: "https://yandex.ru/business/statistic/company/138890152139", expect: "Статистика" },
  { name: "ВКонтакте", url: "https://vk.ru/s_sflowers", expect: "Silver Song" },
  { name: "Авито", url: "https://www.avito.ru/profile/pro/items", expect: "Личный кабинет" },
  { name: "Flowwow", url: "https://flowwow.com/en/shop/silversong-flowersf-4152/", expect: "Flowwow" },
];

(async () => {
  if (cmd === "tabs") {
    (await pages()).forEach((t, i) => console.log(`${i}\t${t.title.slice(0, 60)}\t${t.url.slice(0, 90)}`));
    return;
  }

  if (cmd === "login-status") {
    for (const c of CABINETS) {
      const ok = await withPage(async (send) => {
        await send("Page.navigate", { url: c.url });
        await sleep(6000);
        const r = await send("Runtime.evaluate", { expression: "document.title + ' || ' + location.href", returnByValue: true });
        const txt = String(r.result.value || "");
        return txt;
      });
      const auth = /passport|авторизац|вход|login/i.test(ok) && !/Flowwow|Silver Song|Авито|Статистика/.test(ok);
      console.log(`${auth ? "✗" : "✓"} ${c.name}: ${ok.slice(0, 110)}`);
    }
    return;
  }

  if (cmd === "new") {
    const url = args[1];
    const res = await fetch(`${BASE}/json/new?${encodeURIComponent(url)}`, { method: "PUT" });
    console.log(res.ok ? "открыта вкладка" : `ошибка ${res.status}`);
    return;
  }

  if (cmd === "close") {
    const list = await pages();
    const t = list[Number(args[1]) || 0];
    if (!t) {
      console.log("нет такой вкладки");
      return;
    }
    await fetch(`${BASE}/json/close/${t.id}`);
    console.log("закрыта", t.url.slice(0, 60));
    return;
  }

  if (cmd === "open") {
    const url = args[1];
    const wait = Number(flag("wait", 6000));
    const info = await withPage(async (send) => {
      await send("Page.navigate", { url });
      await sleep(wait);
      const r = await send("Runtime.evaluate", { expression: "document.title + ' || ' + location.href", returnByValue: true });
      return r.result.value;
    });
    console.log("открыто:", info);
    return;
  }

  if (cmd === "text") {
    const target = args[1];
    const wait = Number(flag("wait", target === "-" ? 1000 : 6000));
    const out = flag("out", "");
    const text = await withPage(async (send) => {
      if (target !== "-") {
        await send("Page.navigate", { url: target });
      }
      await sleep(wait);
      const r = await send("Runtime.evaluate", {
        expression: `(document.title || "") + "\\n" + location.href + "\\n---\\n" + (document.body ? document.body.innerText : "")`,
        returnByValue: true,
      });
      return r.result.value || "";
    });
    if (out) {
      await fs.writeFile(out, text);
      console.log("сохранено:", out, text.length, "символов");
    } else {
      console.log(text);
    }
    return;
  }

  if (cmd === "shot") {
    const out = args[1];
    const url = flag("url", "");
    const wait = Number(flag("wait", url ? 6000 : 800));
    await withPage(async (send) => {
      if (url) {
        await send("Page.navigate", { url });
      }
      await sleep(wait);
      const r = await send("Page.captureScreenshot", { format: "png" });
      await fs.writeFile(out, Buffer.from(r.data, "base64"));
    });
    console.log("снимок:", out);
    return;
  }

  if (cmd === "eval") {
    const value = await withPage(async (send) => {
      const r = await send("Runtime.evaluate", { expression: args[1], returnByValue: true, awaitPromise: true, userGesture: true });
      return r.result?.value ?? r.result;
    });
    console.log(typeof value === "string" ? value : JSON.stringify(value, null, 2));
    return;
  }

  console.log("неизвестная команда:", cmd);
  process.exit(2);
})().catch((e) => {
  console.error("ошибка:", e.message);
  process.exit(1);
});
