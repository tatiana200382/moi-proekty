#!/usr/bin/env node
// Клиент seller API Flowwow. Только чтение: перечисленные ниже методы.
// Токен: переменная FLOWWOW_TOKEN или файл ~/.config/flowwow/token (права 600).
// Использование:
//   node flowwow-api.mjs ping
//   node flowwow-api.mjs shops
//   node flowwow-api.mjs products 4152 --stats
//   node flowwow-api.mjs reviews 4152
//   node flowwow-api.mjs stocks 4152 offer-1 offer-2

import { readFileSync } from "node:fs";
import { homedir } from "node:os";
import { join } from "node:path";

const BASE = "https://apis.flowwow.com";
const args = process.argv.slice(2);
const cmd = args[0];
const TOKEN_FILE = join(homedir(), ".config", "flowwow", "token");

function token() {
  if (process.env.FLOWWOW_TOKEN) return process.env.FLOWWOW_TOKEN.trim();
  try {
    return readFileSync(TOKEN_FILE, "utf8").trim();
  } catch {
    console.error(
      `Нет токена. Положите его в ${TOKEN_FILE} (chmod 600) или в FLOWWOW_TOKEN.`
    );
    process.exit(2);
  }
}

async function call(path, { method = "POST", body, auth = true } = {}) {
  const headers = { "Content-Type": "application/json" };
  if (auth) headers.Authorization = `Bearer ${token()}`;
  const res = await fetch(BASE + path, {
    method,
    headers,
    body: body ? JSON.stringify(body) : undefined,
  });
  const text = await res.text();
  let data;
  try {
    data = JSON.parse(text);
  } catch {
    data = text;
  }
  if (!res.ok) {
    console.error(`HTTP ${res.status}:`, JSON.stringify(data, null, 2));
    process.exit(1);
  }
  console.log(JSON.stringify(data, null, 2));
}

const shopId = Number(args[1]);

switch (cmd) {
  case "ping":
    await call("/apiseller/ping/check?say=hello", { method: "GET", auth: false });
    break;
  case "shops":
    await call("/apiseller/shops", { body: { status: "active" } });
    break;
  case "products": {
    if (!shopId) throw new Error("нужен shopId: products <shopId>");
    const withStats = args.includes("--stats");
    await call(`/apiseller/products?shopId=${shopId}`, {
      body: { withStats, limit: 50, page: 0 },
    });
    break;
  }
  case "reviews":
    if (!shopId) throw new Error("нужен shopId: reviews <shopId>");
    await call(`/apiseller/shops/review?shopId=${shopId}&limit=20&sort=date_desc`, {
      method: "GET",
    });
    break;
  case "stocks": {
    const offers = args.slice(2).map((offerId) => ({ offerId }));
    if (!shopId || !offers.length) throw new Error("stocks <shopId> <offerId...>");
    await call(`/apiseller/stocks/get?shopId=${shopId}`, { body: { offers } });
    break;
  }
  default:
    console.error(
      "Команды: ping | shops | products <shopId> [--stats] | reviews <shopId> | stocks <shopId> <offerId...>"
    );
    process.exit(2);
}
