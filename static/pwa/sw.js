
const CACHE = "txenda-shell-v1";
const OFFLINE_URL = "/offline/";
const APP_SHELL = [OFFLINE_URL, "/static/pwa/manifest.webmanifest"];

self.addEventListener("install", event => {
  event.waitUntil(caches.open(CACHE).then(cache => cache.addAll(APP_SHELL)));
  self.skipWaiting();
});
self.addEventListener("activate", event => {
  event.waitUntil((async () => {
    const keys = await caches.keys();
    await Promise.all(keys.filter(k => k !== CACHE).map(k => caches.delete(k)));
    await self.clients.claim();
  })());
});

// Cacheia apenas recursos GET. Páginas privadas usam network-first e fallback offline.
self.addEventListener("fetch", event => {
  const req = event.request;
  const url = new URL(req.url);
  if (url.origin !== self.location.origin) return;

  if (req.method === "POST") {
    event.respondWith((async () => {
      try {
        return await fetch(req.clone());
      } catch (err) {
        await queueRequest(req);
        return new Response(
          "<!doctype html><meta charset='utf-8'><title>TXENDA</title><h2>Pedido guardado neste dispositivo</h2><p>Será reenviado quando a ligação regressar. Mantenha este navegador e os dados do site.</p><a href='/'>Voltar ao TXENDA</a>",
          {headers: {"Content-Type": "text/html; charset=utf-8"}, status: 202}
        );
      }
    })());
    return;
  }

  if (req.method === "GET" && url.origin === self.location.origin) {
    event.respondWith((async () => {
      try {
        const response = await fetch(req);
        if (response.ok && (url.pathname.startsWith("/static/") || url.pathname === OFFLINE_URL)) {
          const cache = await caches.open(CACHE);
          cache.put(req, response.clone());
        }
        return response;
      } catch (err) {
        const cached = await caches.match(req);
        if (cached) return cached;
        if (req.mode === "navigate") return (await caches.match(OFFLINE_URL));
        return new Response("", {status: 503});
      }
    })());
  }
});

function openQueueDB() {
  return new Promise((resolve, reject) => {
    const request = indexedDB.open("txenda-pending", 1);
    request.onupgradeneeded = () => request.result.createObjectStore("requests", {keyPath: "id", autoIncrement: true});
    request.onsuccess = () => resolve(request.result);
    request.onerror = () => reject(request.error);
  });
}
async function queueRequest(request) {
  const db = await openQueueDB();
  const body = await request.clone().text();
  const headers = {};
  request.headers.forEach((v, k) => headers[k] = v);
  await new Promise((resolve, reject) => {
    const tx = db.transaction("requests", "readwrite");
    tx.objectStore("requests").add({url: request.url, method: request.method, headers, body, created: Date.now()});
    tx.oncomplete = resolve; tx.onerror = () => reject(tx.error);
  });
  db.close();
  try { await self.registration.sync.register("txenda-sync"); } catch (_) {}
}
async function replayQueue() {
  const db = await openQueueDB();
  const items = await new Promise((resolve, reject) => {
    const tx = db.transaction("requests", "readonly");
    const req = tx.objectStore("requests").getAll();
    req.onsuccess = () => resolve(req.result); req.onerror = () => reject(req.error);
  });
  for (const item of items) {
    try {
      const response = await fetch(item.url, {
        method: item.method, headers: item.headers, body: item.body,
        credentials: "same-origin", redirect: "follow"
      });
      // 2xx/3xx significa que o servidor recebeu o pedido. 4xx fica pendente
      // para evitar perda silenciosa, por exemplo quando a sessão expirou.
      if (response.ok || (response.status >= 300 && response.status < 400)) {
        await new Promise((resolve, reject) => {
          const tx = db.transaction("requests", "readwrite");
          tx.objectStore("requests").delete(item.id);
          tx.oncomplete = resolve; tx.onerror = () => reject(tx.error);
        });
      }
    } catch (_) { break; }
  }
  db.close();
}
self.addEventListener("sync", event => {
  if (event.tag === "txenda-sync") event.waitUntil(replayQueue());
});
self.addEventListener("message", event => {
  if (event.data === "SYNC_NOW") event.waitUntil(replayQueue());
});
self.addEventListener("online", () => replayQueue());
