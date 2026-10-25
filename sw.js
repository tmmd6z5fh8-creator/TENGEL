// テンゲルⅢ：電波がなくても開けるようにする。ネットにつながったら、いつも最新の版を読む
// （記録・買い目・基盤データはiPhoneの中のデータベースにあって、ここでは触らない）
const CACHE = 'tengel3-2026.10.25-4-2026-10-09b';
// 説明書の写真は別のしまい場所（写真が変わったときだけ入れ直す。アプリの更新のたびには読まない）
const MCACHE = 'tengel3-manual-857ba1af';
const SHELL = ['./', './index.html', './manual.html', './manifest.webmanifest', './icon3-180.png', './icon3-192.png', './icon3-512.png', './icon3-maskable-512.png', './cm/poster.jpg?v=867c5e22'];
const MANUAL = ['./manual/banner.webp', './manual/emblem-160.webp', './manual/s_bottom_bars.webp', './manual/s_judge_info.webp', './manual/s_judge_odds.webp', './manual/s_judge_tri.webp', './manual/s_md_export.webp', './manual/s_md_form.webp', './manual/s_md_list.webp', './manual/s_md_merge.webp', './manual/s_md_record.webp', './manual/s_md_tools.webp', './manual/s_ocr_need.webp', './manual/s_pick_after.webp', './manual/s_pick_before.webp', './manual/s_record_1.webp', './manual/s_record_2.webp', './manual/s_record_open.webp', './manual/s_records.webp', './manual/s_result_a1.webp', './manual/s_result_a2.webp', './manual/s_result_c.webp', './manual/s_set_backup.webp', './manual/s_set_mother.webp', './manual/s_set_ocr.webp', './manual/s_set_update.webp', './manual/s_set_zone.webp', './manual/s_set_zone_save.webp', './manual/s_st_hit.webp', './manual/s_st_notbought.webp', './manual/s_st_notpicked.webp', './manual/s_st_outside.webp', './manual/s_st_wait.webp', './manual/s_stats_money.webp', './manual/s_stats_period.webp', './manual/s_stats_t1.webp', './manual/s_stats_type.webp', './manual/s_tabbar.webp', './manual/s_update_bar.webp', './manual/s_w5_race.webp', './manual/s_w5_res.webp', './manual/s_w5_top.webp'];
self.addEventListener('install', e => {
  const shell = caches.open(CACHE).then(c => c.addAll(SHELL.map(u => new Request(u, { cache: 'reload' })))).then(() => self.skipWaiting());
  // 説明書の写真：まだないものだけ読む。読めなくてもアプリの更新は止めない
  const man = caches.open(MCACHE).then(c => Promise.all(MANUAL.map(u => c.match(u).then(h => h || c.add(u)).catch(() => null)))).catch(() => null);
  e.waitUntil(Promise.all([shell, man]));
});
self.addEventListener('activate', e => { e.waitUntil(caches.keys().then(ks => Promise.all(ks.filter(k => k !== CACHE && k !== MCACHE).map(k => caches.delete(k)))).then(() => self.clients.claim())); });
self.addEventListener('fetch', e => {
  if (e.request.method !== 'GET') return;
  const u = new URL(e.request.url);
  if (u.origin === location.origin && u.pathname.endsWith('/version.json')) return; // 更新の確認は毎回ネットへ
  if (e.request.mode === 'navigate') {
    // ページごとにしまう（説明書を開いても、アプリのページは上書きしない）
    const key = /\/manual\.html$/.test(u.pathname) ? './manual.html' : './index.html';
    e.respondWith(fetch(u.href, { cache: 'no-cache', credentials: 'same-origin' }).then(r => { if (r.ok) { const c = r.clone(); caches.open(CACHE).then(x => x.put(key, c)); } return r; })
      .catch(() => caches.match(key).then(h => h || caches.match('./index.html')).then(h => h || caches.match('./'))));
    return;
  }
  // CMの動画は大きいのでしまわない（iPhoneが少しずつ読む＝Rangeのまま、ブラウザにまかせる）
  if (u.origin === location.origin && /\/cm\/[^/]+\.mp4$/.test(u.pathname)) return;
  if (u.origin === location.origin && /\/manual\/[^/]+$/.test(u.pathname)) {
    e.respondWith(caches.open(MCACHE).then(c => c.match(e.request).then(hit => hit || fetch(e.request).then(r => { if (r.ok) c.put(e.request, r.clone()); return r; }))));
    return;
  }
  if (u.origin === location.origin || /fonts\.(googleapis|gstatic)\.com$/.test(u.hostname)) {
    e.respondWith(caches.match(e.request).then(hit => hit || fetch(e.request).then(r => { if (r.ok || r.type === 'opaque') { const c = r.clone(); caches.open(CACHE).then(x => x.put(e.request, c)); } return r; })));
  }
});
