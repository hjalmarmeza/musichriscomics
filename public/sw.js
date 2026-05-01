const CACHE_NAME = 'musichris-comic-v1';
const ASSETS = [
  '/musichriscomics/',
  '/musichriscomics/index.html',
  '/musichriscomics/manifest.json',
  '/musichriscomics/logo_v4.png'
];

self.addEventListener('install', (event) => {
  event.waitUntil(
    caches.open(CACHE_NAME).then((cache) => cache.addAll(ASSETS))
  );
});

self.addEventListener('fetch', (event) => {
  event.respondWith(
    caches.match(event.request).then((response) => {
      return response || fetch(event.request);
    })
  );
});
