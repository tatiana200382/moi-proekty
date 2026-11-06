#!/usr/bin/env node
// Минимальный клиент Chrome DevTools Protocol для управления окном браузера.
// Использование:
//   node cdp.mjs targets
//   node cdp.mjs goto <url> [targetIndex]
//   node cdp.mjs eval "<js>" [targetIndex]
//   node cdp.mjs cookies [targetIndex]
//   node cdp.mjs shot <out.png> [targetIndex]

const args = process.argv.slice(2);
const cmd = args[0] || "targets";
const PORT = process.env.CDP_PORT || 9222;

async function targets() {
  const res = await fetch(`http://localhost:${PORT}/json/list`);
  return res.json();
}

async function pickPage(index = 0) {
  const list = await targets();
  const pages = list.filter((t) => t.type === "page");
  const t = pages[index] || pages[0];
  if (!t) throw new Error("нет вкладок");
  return t;
}

async function connect(wsUrl) {
  const ws = new WebSocket(wsUrl);
  await new Promise((resolve, reject) => {
    ws.addEventListener("open", resolve, { once: true });
    ws.addEventListener("error", reject, { once: true });
  });
  let id = 0;
  const pending = new Map();
  ws.addEventListener("message", (ev) => {
    const msg = JSON.parse(ev.data);
    if (msg.id && pending.has(msg.id)) {
      const { resolve, reject } = pending.get(msg.id);
      pending.delete(msg.id);
      msg.error ? reject(new Error(JSON.stringify(msg.error))) : resolve(msg.result);
    }
  });
  const send = (method, params = {}) =>
    new Promise((resolve, reject) => {
      const mid = ++id;
      pending.set(mid, { resolve, reject });
      ws.send(JSON.stringify({ id: mid, method, params }));
      setTimeout(() => {
        if (pending.has(mid)) {
          pending.delete(mid);
          reject(new Error(`таймаут ${method}`));
        }
      }, 30000);
    });
  return { ws, send };
}

const sleep = (ms) => new Promise((r) => setTimeout(r, ms));

(async () => {
  if (cmd === "targets") {
    const list = await targets();
    list.forEach((t, i) => console.log(i, t.type, t.url.slice(0, 90)));
    return;
  }

  const idx = Number(args[args.length - 1]) || 0;
  const page = await pickPage(Number.isInteger(idx) && args.length > 2 ? idx : 0);
  const { ws, send } = await connect(page.webSocketDebuggerUrl);

  try {
    if (cmd === "goto") {
      const url = args[1];
      await send("Page.enable");
      await send("Page.navigate", { url });
      await sleep(4000);
      console.log("открыто:", url);
    } else if (cmd === "eval") {
      const r = await send("Runtime.evaluate", {
        expression: args[1],
        returnByValue: true,
        awaitPromise: true,
        userGesture: true,
      });
      console.log(JSON.stringify(r.result?.value ?? r.result, null, 2));
    } else if (cmd === "evalfile") {
      const fs = await import("node:fs/promises");
      const src = await fs.readFile(args[1], "utf-8");
      const r2 = await send("Runtime.evaluate", {
        expression: src,
        returnByValue: true,
        awaitPromise: true,
        userGesture: true,
      });
      console.log(typeof r2.result?.value === "string" ? r2.result.value : JSON.stringify(r2.result, null, 2));
    } else if (cmd === "cookies") {
      await send("Network.enable");
      const r = await send("Network.getAllCookies");
      const need = ["Session_id", "sessionid2", "session_id", "L", "yandex_login"];
      const found = r.cookies.filter((c) => need.includes(c.name));
      for (const c of found) {
        console.log(`${c.name}\t${c.domain}\t${c.value.length} символов`);
      }
      if (!found.length) console.log("нужных куки нет — вероятно, не выполнен вход");
    } else if (cmd === "shot") {
      await send("Page.enable");
      const r = await send("Page.captureScreenshot", { format: "png" });
      const fs = await import("node:fs/promises");
      await fs.writeFile(args[1], Buffer.from(r.data, "base64"));
      console.log("снимок сохранён:", args[1]);
    } else {
      console.log("неизвестная команда:", cmd);
    }
  } finally {
    ws.close();
    setTimeout(() => process.exit(0), 250);
  }
})().catch((e) => {
  console.error("ошибка:", e.message);
  process.exit(1);
});
