import fs from "node:fs/promises";
const list = await (await fetch("http://localhost:9224/json/list")).json();
const page = list.find((t) => t.type === "page");
if (!page) throw new Error("нет вкладок");
const ws = new WebSocket(page.webSocketDebuggerUrl);
await new Promise((res, rej) => { ws.addEventListener("open", res, { once: true }); ws.addEventListener("error", rej, { once: true }); });
let id = 0; const pending = new Map();
ws.addEventListener("message", (ev) => {
  const m = JSON.parse(ev.data);
  if (m.id && pending.has(m.id)) { const p = pending.get(m.id); pending.delete(m.id); m.error ? p.reject(new Error(JSON.stringify(m.error))) : p.resolve(m.result); }
});
const send = (method, params = {}) => new Promise((resolve, reject) => {
  const mid = ++id; pending.set(mid, { resolve, reject });
  ws.send(JSON.stringify({ id: mid, method, params }));
  setTimeout(() => { if (pending.has(mid)) { pending.delete(mid); reject(new Error("timeout " + method)); } }, 20000);
});
await send("Network.enable");
const r = await send("Network.getAllCookies");
const av = r.cookies.filter((c) => (c.domain || "").includes("avito"));
console.log("avito cookies:", av.length);
for (const c of av.slice(0, 40)) console.log(c.name, "|", c.domain, "|", String(c.value).length, "|", c.expires);
const state = {
  cookies: av.map((c) => ({
    name: c.name, value: c.value, domain: c.domain, path: c.path || "/",
    expires: typeof c.expires === "number" ? c.expires : -1,
    httpOnly: !!c.httpOnly, secure: !!c.secure,
    sameSite: c.sameSite === "None" ? "None" : c.sameSite === "Strict" ? "Strict" : "Lax",
  })),
  origins: [],
};
await fs.writeFile("/tmp/avito-mac-state.json", JSON.stringify(state, null, 1));
console.log("saved /tmp/avito-mac-state.json");
ws.close(); setTimeout(() => process.exit(0), 200);
