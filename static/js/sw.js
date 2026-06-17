const CACHE = 'gymtracker-v1';
const SHELL = [
  '/',
  '/static/css/main.css',
  '/static/js/app.js',
];

self.addEventListener('install', function(e) {
  e.waitUntil(
    caches.open(CACHE).then(function(c) {
      return c.addAll(SHELL);
    })
  );
  self.skipWaiting();
});

self.addEventListener('activate', function(e) {
  e.waitUntil(
    caches.keys().then(function(keys) {
      return Promise.all(
        keys.filter(function(k) { return k !== CACHE; }).map(function(k) { return caches.delete(k); })
      );
    })
  );
  self.clients.claim();
});

self.addEventListener('fetch', function(e) {
  var req = e.request;

  // Skip non-GET and API/POST requests
  if (req.method !== 'GET') return;
  if (req.url.includes('/admin/')) return;

  // Cache-first for static assets
  if (req.url.includes('/static/')) {
    e.respondWith(
      caches.match(req).then(function(r) { return r || fetch(req); })
    );
    return;
  }

  // Network-first for pages, fallback to cache
  e.respondWith(
    fetch(req)
      .then(function(res) {
        var clone = res.clone();
        caches.open(CACHE).then(function(c) { c.put(req, clone); });
        return res;
      })
      .catch(function() { return caches.match(req); })
  );
});
