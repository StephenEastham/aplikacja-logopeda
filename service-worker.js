const CACHE_NAME = "logopeda-v32";
const APP_FILES = [
  "./",
  "./index.html",
  "./app.css",
  "./app.js",
  "./manifest.webmanifest",
  "./assets/assets.md",
  "./assets/images/pa_papuga.svg",
  "./assets/images/icon-192.png",
  "./assets/images/icon-512.png",
  "./assets/sounds/pa_papuga.wav",
];

async function cacheAppFiles() {
  const cache = await caches.open(CACHE_NAME);
  await Promise.all(APP_FILES.map((url) => cache.add(new Request(url, { cache: "reload" }))));

  const assetMapUrl = new URL("./assets/assets.md", self.registration.scope);
  const response = await fetch(assetMapUrl);
  const markdown = await response.text();
  const assetUrls = new Set(
    [...markdown.matchAll(/\]\((\.\/(?:images|sounds)\/[^)]+)\)/g)]
      .map((match) => new URL(match[1], assetMapUrl).href),
  );
  await Promise.all(
    [...assetUrls].map((url) => cache.add(new Request(url, { cache: "reload" }))),
  );
}

self.addEventListener("install", (event) => {
  event.waitUntil(cacheAppFiles());
  self.skipWaiting();
});

self.addEventListener("activate", (event) => {
  event.waitUntil(
    caches
      .keys()
      .then((keys) => Promise.all(keys.filter((key) => key !== CACHE_NAME).map((key) => caches.delete(key))))
      .then(() => self.clients.claim()),
  );
});

self.addEventListener("fetch", (event) => {
  if (event.request.method !== "GET") {
    return;
  }

  if (event.request.mode === "navigate") {
    event.respondWith(
      fetch(event.request).catch(() => caches.match(new URL("./index.html", self.registration.scope))),
    );
    return;
  }

  event.respondWith(
    caches.match(event.request).then((cachedResponse) => {
      return cachedResponse || fetch(event.request);
    }),
  );
});