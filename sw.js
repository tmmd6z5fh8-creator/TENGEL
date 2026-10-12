// テンゲルⅢ：電波がなくても開けるようにする。ネットにつながったら、いつも最新の版を読む
// （記録・買い目・基盤データはiPhoneの中のデータベースにあって、ここでは触らない）
const CACHE = 'tengel3-2026.10.12-2-2026-10-09b';
const SHELL = ['./', './index.html', './manifest.webmanifest', './icon3-180.png', './icon3-192.png', './icon3-512.png', './icon3-maskable-512.png'];
self.addEventListener('install', e => { e.waitUntil(caches.open(CACHE).then(c => c.addAll(SHELL.map(u => new Request(u, { cache: 'reload' })))).then(() => self.skipWaiting())); });
self.addEventListener('activate', e => { e.waitUntil(caches.keys().then(ks => Promise.all(ks.filter(k => k !== CACHE).map(k => caches.delete(k)))).then(() => self.clients.claim())); });
self.addEventListener('fetch', e => {
  if (e.request.method !== 'GET') return;
  const u = new URL(e.request.url);
  if (u.origin === location.origin && u.pathname.endsWith('/version.json')) return; // 更新の確認は毎回ネットへ
  if (e.request.mode === 'navigate') {
    e.respondWith(fetch(u.href, { cache: 'no-cache', credentials: 'same-origin' }).then(r => { if (r.ok) { const c = r.clone(); caches.open(CACHE).then(x => x.put('./index.html', c)); } return r; })
      .catch(() => caches.match('./index.html').then(h => h || caches.match('./'))));
    return;
  }
  if (u.origin === location.origin || /fonts\.(googleapis|gstatic)\.com$/.test(u.hostname)) {
    e.respondWith(caches.match(e.request).then(hit => hit || fetch(e.request).then(r => { if (r.ok || r.type === 'opaque') { const c = r.clone(); caches.open(CACHE).then(x => x.put(e.request, c)); } return r; })));
  }
});
