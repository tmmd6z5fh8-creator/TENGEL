// テンゲル iOSアプリの自動テスト（GitHubのMacのシミュレーターで動かす。アプリには入れない）
// CI（run.sh）が先頭に window.__ST_PHASE（1〜3）と window.__ST_DEVICE（iphone／ipad）を足して、アプリの Documents/selftest.js に置く。
// アプリ（Debug）は -tengelSelfTest で起動したときだけ、これを各ページの最初に入れる。
// 結果は window.webkit.messageHandlers.tengel に { name:'selftest', payload:{ file, text } } で渡す → アプリが Documents/ に書く。
//   mark-<名前>.txt … CIがスクショを撮る合図（出したあと2.5秒そのままにする）
//   report-<名前>.json … 結果
// 1回目：記録を1件保存（マザーデータにも入る）→ 自動バックアップ・App Storeの版・データの更新（GitHub Pages）・画像の読み取り（端末の中の文字認識：ci/ocr/ の架空のオッズ画面）・
//        時計・電波に重なる分の測り方・CMの動画・フォント・コピーを確かめて、設定・CM・記録・説明書を見せる
// 2回目：開き直しても記録が残っているか → 保存場所（IndexedDB）を消す
// 3回目：「前の記録が見つかったよ」→「記録を戻す」で戻るか
(function () {
  'use strict';
  if (window.top !== window) return;
  var PH = window.__ST_PHASE || 1, DEV = window.__ST_DEVICE || 'iphone';
  var errs = [];
  window.addEventListener('error', function (e) { errs.push(String(e.message || e) + ' @' + String(e.filename || '').split('/').pop() + ':' + e.lineno); });
  window.addEventListener('unhandledrejection', function (e) { var r = e.reason; errs.push('rejection: ' + String(r && (r.message || r.code) || r)); });
  function post(file, text) { try { window.webkit.messageHandlers.tengel.postMessage({ id: 0, name: 'selftest', payload: { file: file, text: text } }); } catch (e) { /* アプリとつながっていない */ } }
  var sleep = function (ms) { return new Promise(function (r) { setTimeout(r, ms); }); };
  async function waitFor(fn, ms) { var t0 = Date.now(); while (Date.now() - t0 < (ms || 15000)) { try { var v = fn(); if (v) return v; } catch (e) { /* まだ */ } await sleep(150); } return null; }
  // スクショの合図 → CIが撮り終わって ack-<名前>.txt を置くまで待つ（アプリが __selftest/ で読ませる。最長60秒）
  async function mark(name) {
    post('mark-' + name + '.txt', String(Date.now()));
    var t0 = Date.now();
    while (Date.now() - t0 < 60000) {
      try { var r = await fetch('__selftest/ack-' + name + '.txt', { cache: 'no-store' }); if (r.ok) return; } catch (e) { /* まだ */ }
      await sleep(300);
    }
  }
  function report(name, R) { R.errors = errs.slice(); R.at = new Date().toISOString(); post('report-' + name + '.json', JSON.stringify(R, null, 1)); }
  async function step(R, key, fn) { try { R[key] = await fn(); } catch (e) { R[key] = { exception: String(e && (e.message || e)) }; } }
  function tab(name) {
    var bar = document.querySelector('.tabbar'), vis = bar && getComputedStyle(bar).display !== 'none';
    var b = document.querySelector((vis ? '.tabbar' : '.tabs-top') + ' [data-tab=' + name + ']');
    if (b) b.click(); return !!b;
  }
  function setVal(el, v) {
    var d = Object.getOwnPropertyDescriptor(Object.getPrototypeOf(el), 'value'); d.set.call(el, v);
    el.dispatchEvent(new Event('input', { bubbles: true })); el.dispatchEvent(new Event('change', { bubbles: true }));
  }
  function loaded() { return new Promise(function (r) { if (document.readyState === 'complete') r(); else window.addEventListener('load', function () { r(); }); }); }
  var FORM = { venue: '', date: '2026-10-10', r: '8', dist: '1400', surface: 'ダ', baba: '稍重', n: '14', s1: '41.3', s1combo: '6-2-10', s5: '58.2', s10: '84.0',
    rows: [[1, 12.4, '3.0-4.6'], [2, 4.1, '1.6-2.2'], [3, 31.5, '6.1-9.8'], [4, 9.8, '2.6-3.9'], [5, 18.2, '4.0-6.2'], [6, 2.4, '1.1-1.3'], [7, 7.6, '2.1-3.1'], [8, 54.0, '9.4-15.0'], [9, 25.9, '5.2-8.1'], [10, 6.3, '1.9-2.7'], [11, 14.7, '3.3-5.1'], [12, 88.6, '13.2-21.1'], [13, 40.2, '7.7-12.2'], [14, 120.5, '18.4-29.6']].map(function (x) { return { no: x[0], tan: String(x[1]), fuku: x[2] }; }) };
  var isManual = /manual\.html$/.test(location.pathname);

  async function ready() {
    await loaded();
    await waitFor(function () { return window.TengelLocal; }, 20000);
    await window.TengelLocal.ready.catch(function () {});
    await sleep(1200);
  }
  function basic() {
    var TL = window.TengelLocal;
    var ls; try { localStorage.setItem('st-ls', '1'); ls = localStorage.getItem('st-ls') === '1'; } catch (e) { ls = String(e); }
    return { href: location.href, secure: window.isSecureContext, native: window.__NATIVE, info: window.__NATIVE_INFO || null, bridge: !!window.TengelNative,
      memOnly: TL ? TL.memOnly() : 'no TengelLocal', races: TL ? TL.mem.races.size : -1, bets: TL ? TL.mem.bets.size : -1, sw: 'serviceWorker' in navigator, ls: ls,
      clipboard: !!(navigator.clipboard && navigator.clipboard.writeText), ver: (document.querySelector('.brand .ver') || {}).textContent || '', ua: navigator.userAgent,
      w: innerWidth, h: innerHeight, dpr: devicePixelRatio, dark: matchMedia('(prefers-color-scheme: dark)').matches,
      safeTop: getComputedStyle(document.documentElement).paddingTop, safeBottom: getComputedStyle(document.documentElement).paddingBottom };
  }

  async function phase1() {
    if (sessionStorage.getItem('st1') === 'done') return backFromManual();
    if (!sessionStorage.getItem('st1')) {
      // 判定タブにレースを入れておく（Web版のテストと同じ入れ方）→ 開き直す
      await loaded();
      localStorage.setItem('tengel.form', JSON.stringify(FORM)); sessionStorage.setItem('st1', 'seeded');
      location.reload(); return;
    }
    await ready();
    var R = { phase: 1, device: DEV };
    R.basic = basic();
    await mark('main');
    await step(R, 'save', async function () {
      var card = document.querySelector('#recCard');
      setVal(card.querySelector('[data-k=stake][data-t="馬単"]'), '1800');
      setVal(card.querySelector('[data-k=res]'), '7-6-2');
      setVal(card.querySelector('[data-k=payout][data-t="馬単"]'), '5230');
      await sleep(300); card.querySelector('[data-act=save]').click();
      await waitFor(function () { return TengelLocal.mem.bets.size > 0; }, 8000);
      return { bets: TengelLocal.mem.bets.size, ids: Array.from(TengelLocal.mem.bets.keys()), toast: (document.querySelector('#toast') || {}).textContent };
    });
    await sleep(2800);
    await step(R, 'autobackup', async function () {
      var s = await TengelNative.loadBackup();
      return s ? { n: (s.bets || []).length, at: s.at, auto: s.auto, ids: (s.bets || []).map(function (b) { return b.id; }), keys: Object.keys(s), hasKey: JSON.stringify(s).indexOf('sk-ant') >= 0 } : null;
    });
    await step(R, 'copy', function () { return TengelNative.copy('テンゲルのテスト'); });
    await step(R, 'downloads', async function () { return !!(await window.claude.use('downloads')); });
    // 画像の読み取り：端末の中の文字認識（Vision）で、架空のオッズ画面（単勝・複勝＋3連単の人気順）を読んで入力欄の形にする。外には何も送らない
    await step(R, 'ocr', async function () {
      var files = [];
      for (var i = 0; i < 2; i++) {
        var nm = ['a_tanfuku_waku.jpg', 'c_sanrentan.jpg'][i];
        var res = await fetch('__selftest/' + nm, { cache: 'no-store' });
        if (!res.ok) return { skipped: 'no sample ' + nm + ' (' + res.status + ')' };
        files.push(new File([await res.blob()], nm, { type: 'image/jpeg' }));
      }
      var sample = await window.claude.use('sample');
      var t0 = Date.now();
      var raw = await TengelNative.readText(await new Promise(function (ok, ng) { var fr = new FileReader(); fr.onload = function () { ok(String(fr.result).split(',')[1]); }; fr.onerror = ng; fr.readAsDataURL(files[0]); }));
      var d = await sample.json('', { images: files });
      var hs = d.horses || [];
      return { local: !!sample.local, ms: Date.now() - t0, raw: { ok: raw && raw.ok, n: raw && raw.lines ? raw.lines.length : -1, ms: raw && raw.ms, sample: (raw && raw.lines || []).slice(0, 6).map(function (l) { return l.text; }) },
        venue: d.venue, date: d.date, r: d.r, dist: d.dist, surface: d.surface, baba: d.baba, n: d.n, horses: hs.length, h6: hs.find(function (h) { return h.no === 6; }) || null, h12: hs.find(function (h) { return h.no === 12; }) || null,
        s1: d.s1, s5: d.s5, s10: d.s10, docs: d._docs, lines: d._lines };
    });
    await step(R, 'layout', async function () { var L = await TengelNative.layout(); L.cssTop = getComputedStyle(document.documentElement).getPropertyValue('--top-inset'); L.cssBottom = getComputedStyle(document.documentElement).getPropertyValue('--bottom-inset'); L.padTop = getComputedStyle(document.documentElement).paddingTop; L.padBottom = getComputedStyle(document.documentElement).paddingBottom; return L; });
    // App Storeの版（アプリがAppleに聞く）・データの更新（GitHub Pages を tengel:// から読めるか＝CORS）・マザーデータに入ったか
    await step(R, 'store', async function () { return await TengelNative.storeInfo(); });
    await step(R, 'data', async function () {
      try { var d = await TengelLocal.data.check(); return { ok: true, ver: d.ver, n: d.n, newer: d.newer, cur: d.cur }; }
      catch (e) { return { ok: false, msg: String(e && e.message || e), url: TengelLocal.data.url() }; }
    });
    await step(R, 'mother', function () { var r = TengelLocal.slots.rows(1).filter(function (x) { return x.src; }); return { n: TengelLocal.slots.rows(1).length, input: r.map(function (x) { return x.id + ' ' + x.p1 + '-' + x.p2 + '-' + x.p3; }) }; });
    await step(R, 'fonts', async function () {
      await Promise.race([document.fonts.ready, sleep(8000)]);
      var fams = {}; document.fonts.forEach(function (f) { if (f.status === 'loaded') fams[f.family] = 1; });
      return { status: document.fonts.status, loaded: Object.keys(fams) };
    });
    await step(R, 'video', function () {
      return new Promise(function (res) {
        var v = document.createElement('video'); v.muted = true; v.preload = 'metadata';
        v.src = new URL(window.__CM.src, 'https://tmmd6z5fh8-creator.github.io/TENGEL/').href;
        var t = setTimeout(function () { res({ timeout: true, rs: v.readyState, err: v.error && v.error.code, src: v.src }); }, 20000);
        v.onloadedmetadata = function () { clearTimeout(t); res({ ok: true, dur: v.duration, w: v.videoWidth, h: v.videoHeight }); };
        v.onerror = function () { clearTimeout(t); res({ error: v.error && v.error.code, src: v.src }); };
        v.load();
      });
    });
    // 設定タブ
    tab('set'); await sleep(900);
    var up = document.querySelector('#setUpdate'); if (up) up.scrollIntoView({ block: 'start' }); await sleep(600);
    var nc = document.querySelector('#nuCheck'); if (nc) nc.click();
    var sc = document.querySelector('#sdCheck'); if (sc) sc.click();
    await sleep(4000);
    R.settings = { update: up ? up.innerText : null, data: (document.querySelector('#setData') || {}).innerText || null, cmPoster: (function () { var i = document.querySelector('#setCM img'); return i ? i.naturalWidth : -1; })() };
    await mark('settings');
    var bk = document.querySelector('#setBackup'); if (bk) bk.scrollIntoView({ block: 'start' }); await sleep(600);
    R.settings.backup = bk ? bk.innerText : null;
    await mark('backup');
    // このアプリについて（ご利用にあたって・非公式と商標を開く）
    var ab = document.querySelector('#setAbout');
    if (ab) { var sm = ab.querySelector('#abNotice summary'); if (sm) sm.click(); ab.scrollIntoView({ block: 'start' }); }
    await sleep(600);
    R.about = ab ? { text: ab.innerText.slice(0, 1500), fonts: !!ab.querySelector('#abFonts'), tokusho: !!ab.querySelector('#abTokusho') } : null;
    await mark('about');
    // CM（全画面で再生）
    var cmb = document.querySelector('#setCM [data-cm=play]'); if (cmb) cmb.scrollIntoView({ block: 'center' }); await sleep(300);
    if (cmb) cmb.click();
    await step(R, 'cm', async function () {
      var v = await waitFor(function () { return document.querySelector('#cmModal video'); }, 3000);
      if (!v) return { modal: false };
      await waitFor(function () { return v.readyState >= 2 && v.currentTime > 0.3; }, 12000);
      return { modal: true, rs: v.readyState, t: v.currentTime, paused: v.paused, err: v.error && v.error.code, src: v.currentSrc };
    });
    await mark('cm');
    var cl = document.querySelector('#cmModal .cmclose'); if (cl) cl.click(); await sleep(400);
    // 記録タブ
    tab('rec'); await sleep(900); window.scrollTo(0, 0); await sleep(300);
    await mark('rec');
    // 外への通信（Google のフォントなどがないか）
    R.outside = performance.getEntriesByType('resource').map(function (e) { return e.name; }).filter(function (n) { return !/^tengel:/.test(n); });
    report('1', R);
    await sleep(500);
    sessionStorage.setItem('st1', 'done');
    location.href = 'manual.html';
  }
  async function manualPage() {
    await loaded(); await sleep(1500);
    var R = { phase: PH, device: DEV, page: 'manual' };
    var imgs = Array.prototype.slice.call(document.images);
    R.top = { title: document.title, imgs: imgs.length, loaded: imgs.filter(function (i) { return i.complete && i.naturalWidth > 0; }).length };
    await mark('manual');
    location.hash = '#ocr'; await sleep(1500);
    var vis = imgs.filter(function (i) { var r = i.getBoundingClientRect(); return r.width > 0 && r.height > 0; });
    R.item = { hash: location.hash, visible: vis.length, visibleLoaded: vis.filter(function (i) { return i.complete && i.naturalWidth > 0; }).length };
    await mark('manual-item');
    R.toApp = (document.querySelector('#toApp') || {}).href || null;
    report('manual', R);
    await sleep(400);
    location.href = './';   // アプリのページを開き直す（tengel://localhost/ → index.html）
  }
  async function backFromManual() {
    await ready();
    var R = { phase: 1, device: DEV, page: 'back' };
    R.basic = basic();
    await mark('back');
    report('back', R);
  }
  async function phase2() {
    await ready();
    var R = { phase: 2, device: DEV };
    R.basic = basic();
    R.persist = { bets: TengelLocal.mem.bets.size, ids: Array.from(TengelLocal.mem.bets.keys()), form: !!localStorage.getItem('tengel.form') };
    await sleep(2500);
    await step(R, 'autobackup', async function () { var s = await TengelNative.loadBackup(); return s ? { n: (s.bets || []).length, at: s.at } : null; });
    await step(R, 'deleteDB', function () {
      return new Promise(function (res) {
        var q = indexedDB.deleteDatabase('tengel3');
        q.onsuccess = function () { res('ok'); }; q.onerror = function () { res('error ' + q.error); }; q.onblocked = function () { res('blocked'); };
        setTimeout(function () { res('timeout'); }, 8000);
      });
    });
    report('2', R);
  }
  async function phase3() {
    await ready();
    var R = { phase: 3, device: DEV };
    var box = await waitFor(function () { return document.querySelector('#nativeRestore'); }, 20000);
    R.offer = box ? box.innerText : null;
    R.before = { bets: TengelLocal.mem.bets.size, races: TengelLocal.mem.races.size };
    await mark('offer');
    var yes = document.querySelector('#nativeRestore [data-nr=yes]'); if (yes) yes.click();
    await waitFor(function () { return TengelLocal.mem.bets.size > 0; }, 10000);
    await sleep(800);
    R.after = { bets: TengelLocal.mem.bets.size, ids: Array.from(TengelLocal.mem.bets.keys()), toast: (document.querySelector('#toast') || {}).textContent, offer: !!document.querySelector('#nativeRestore') };
    await mark('restored');
    await sleep(1500);
    await step(R, 'autobackup', async function () { var s = await TengelNative.loadBackup(); return s ? { n: (s.bets || []).length, at: s.at } : null; });
    report('3', R);
    // 外のページへのリンク → アプリの中では開かず、Safariで開く（アプリは裏に回る。CIがスクショで確かめる）
    await sleep(500);
    var before = location.href, a = document.createElement('a');
    a.href = 'https://example.com/'; a.textContent = 'example'; document.body.appendChild(a); a.click();
    await sleep(700);
    report('link', { phase: 3, device: DEV, before: before, after: location.href });
  }
  var run = isManual ? manualPage : PH === 2 ? phase2 : PH === 3 ? phase3 : phase1;
  run().catch(function (e) { report('crash-' + (isManual ? 'manual' : PH), { phase: PH, device: DEV, exception: String(e && (e.stack || e.message || e)) }); });
})();
