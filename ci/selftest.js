// テンゲル iOSアプリの自動テスト（GitHubのMacのシミュレーターで動かす。アプリには入れない）
// CI（run.sh）が先頭に window.__ST_PHASE（1〜3）と window.__ST_DEVICE（iphone／ipad）を足して、アプリの Documents/selftest.js に置く。
// アプリ（Debug）は -tengelSelfTest で起動したときだけ、これを各ページの最初に入れる。
// 結果は window.webkit.messageHandlers.tengel に { name:'selftest', payload:{ file, text } } で渡す → アプリが Documents/ に書く。
//   mark-<名前>.txt … CIがスクショを撮る合図（出したあと2.5秒そのままにする）
//   report-<名前>.json … 結果
// 1回目：買い目を予約（記録）→ 的中ボタン（第3弾：デカ・ど的中の演出とボード）→ 自動バックアップ・App Storeの版・データの更新（GitHub Pages）・画像の読み取り（端末の中の文字認識：ci/ocr/ の架空のオッズ画面）・
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

  // アプリを開いた時の画面（19章）：はじめては「はじめる」を押す、2回目からはタップでとばす（その前にスクショ）
  async function gate(shot) {
    var g = await waitFor(function () { var x = document.querySelector('#gate'); return x && !x.hidden ? x : null; }, 4000);
    if (!g) return 'none';
    var kind = document.querySelector('#gateGo') ? 'first' : 'splash';
    if (shot) await mark('gate-' + kind);
    for (var i = 0; i < 20; i++) {
      var go = document.querySelector('#gateGo'); if (go) go.click(); else g.click();
      await sleep(250);
      if (g.hidden) break;
    }
    return kind;
  }
  async function ready() {
    await loaded();
    await waitFor(function () { return window.TengelLocal; }, 20000);
    await window.TengelLocal.ready.catch(function () {});
    await sleep(600);
    window.__gate = await gate(PH === 1 && !sessionStorage.getItem('st1done'));
    if (window.TengelWallet) await window.TengelWallet.ready;
    await sleep(600);
  }
  // ポイント（App Store版）：残高・できごと・キーチェーンのしるし・拡大の状態
  async function wallet() {
    var W = window.TengelWallet; if (!W) return null;
    var m = await TengelNative.marker('get', 'gift-first').catch(function (e) { return { error: String(e) }; });
    var z = await TengelNative.zoom({}).catch(function (e) { return { error: String(e) }; });
    return { total: W.total(), balance: W.balance(), events: W.events().map(function (e) { return e.id + ':' + e.amount; }), counted: W.countedN(), gift: m, zoom: z, viewport: (document.querySelector('meta[name=viewport]') || {}).content, gate: window.__gate };
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
    await step(R, 'wallet', wallet);
    await mark('main');
    // 第2弾：判定画面の下は「買い目」のカード → 「買い目を予約」で記録（bets）に rsv が入る。CIでは通知の許可のダイアログを出さない（お知らせはオフ）
    await step(R, 'notify', async function () { var s = await TengelNative.notify('status'); await TengelLocal.putSetting('notify', false); return s; });
    await step(R, 'save', async function () {
      var card = document.querySelector('#recCard');
      var btn = card.querySelector('[data-rsv=reserve]'); if (!btn) throw new Error('no reserve button: ' + card.innerText.slice(0, 120));
      btn.click();
      await waitFor(function () { return TengelLocal.mem.bets.size > 0; }, 8000);
      await sleep(400);
      var b = Array.from(TengelLocal.mem.bets.values())[0];
      return { bets: TengelLocal.mem.bets.size, ids: Array.from(TengelLocal.mem.bets.keys()), rsv: b && b.rsv ? { state: b.rsv.state, types: b.rsv.types, points: b.rsv.points, zones: b.rsv.zones } : null, card: card.innerText.slice(0, 160), toast: (document.querySelector('#toast') || {}).textContent, reserve: !!window.TengelReserve, rate: !!window.TengelCustomRate, omakase: !!document.querySelector('#omakaseBtn'), pct: Array.from(document.querySelectorAll('#result .zref')).map(function (e) { return e.innerText; }).filter(function (t) { return t.indexOf('選んだ馬で') >= 0; }).slice(0, 2) };
    });
    // 第3弾：的中ボタン。CIの保存は予約まで（結果は入れない）なので、演出を直接出して確かめる：デカ的中の PUSH → タップ → いつものボード／ど的中の PUSH → 結果の画面。
    // 絵と音のファイル（fz_nglow.webp・sfx_*.m4a）はリポジトリに入れないので、CIでは 404（なしでも動くことを確かめる）
    await step(R, 'fx', async function () {
      var F = window.TengelFx; if (!F) return { on: false };
      var spec = { r: 8, n: 14, rows: [{ t: '3連単', state: '的中', hits: [[6, 2, 10]], n: 18 }, { t: '馬単', state: '的中', hits: [[6, 2]], n: 9 }, { t: 'ワイド', state: '不的中', hits: [], n: 9 }], ranks: { 6: 1, 2: 2, 10: 3 } };
      // 画面の 進み（1秒に 何コマ 描けたか）：シミュレーターでは 演出の 間 描くのが 止まる ことが ある（実機で 確かめる）
      function fps(ms) { return new Promise(function (r) { var n = 0, t0 = performance.now(); (function tick() { n++; if (performance.now() - t0 < ms) requestAnimationFrame(tick); else r(Math.round(n * 1000 / ms)); })(); }); }
      var kind = F.show(Object.assign({ force: 'big' }, spec));
      var fpsPush = await fps(1000);
      var res = { kind: kind, fpsPush: fpsPush, push: !!document.querySelector('#fxOv .ov.big .pbox.pz .push'), pz: (document.querySelector('#fxOv .pbox') || { style: { getPropertyValue: function () { return ''; } } }).style.getPropertyValue('--pz'), css: !!document.querySelector('#fxCss'), settings: F.get(), calm: F.calm(), reduced: F.reduced(), sfx: F.sfxState(), assets: {},
        stage: (function () { var st = document.querySelector('#fxOv .fxs'); return st ? { k: st.style.getPropertyValue('--fxk'), w: innerWidth, h: innerHeight } : null; })(),
        decide: [F.decide(Object.assign({}, spec, { ranks: { 6: 1, 2: 2, 10: 11 } })).kind, F.decide(spec).kind, F.decide({ rows: [{ t: '馬単', state: '的中', hits: [[6, 2]] }] }).kind, F.decide({ rows: [{ t: '馬単', state: '不的中', hits: [] }] }).kind] };
      for (var k of ['fz_nglow.webp', 'sfx_big.m4a']) { try { var r = await fetch(k, { cache: 'no-store' }); res.assets[k] = r.status; } catch (e) { res.assets[k] = String(e); } }
      await mark('fx-push');
      F.tap(); res.fpsReveal = await fps(1000);
      await waitFor(function () { var c = document.querySelector('#fxOv .close'); return c && getComputedStyle(c).visibility === 'visible'; }, 6000);
      var rb = document.querySelector('#fxOv .rb');
      res.board = rb ? { cls: rb.className, title: rb.querySelector('.bh').innerText, sub: rb.querySelector('.bsub').innerText, rows: Array.from(rb.querySelectorAll('.brows li')).map(function (li) { return li.innerText.replace(/\s+/g, ' '); }), closeVis: getComputedStyle(document.querySelector('#fxOv .close')).visibility } : null;
      await mark('fx-board');
      F.close(); await sleep(300);
      F.show(Object.assign({ force: 'fz' }, spec, { ranks: { 6: 1, 2: 2, 10: 11 } })); await sleep(600);
      res.fzPush = !!document.querySelector('#fxOv .ov.fz .pbox.pz .push'); res.fzPz = (document.querySelector('#fxOv .pbox') || { style: { getPropertyValue: function () { return ''; } } }).style.getPropertyValue('--pz');
      await mark('fx-fz-push');
      F.tap(); res.fpsFz = await fps(1000); await sleep(6600);
      await waitFor(function () { var c = document.querySelector('#fxOv .close'); return c && getComputedStyle(c).visibility === 'visible'; }, 6000);
      res.fz = { rib: (document.querySelector('#fxOv .rb .zrib') || {}).innerText || null, title: (document.querySelector('#fxOv .rb .bh') || {}).innerText || null, closeVis: getComputedStyle(document.querySelector('#fxOv .close')).visibility, finOpacity: getComputedStyle(document.querySelector('#fxOv .ov.fz .fin')).opacity };
      await mark('fx-fz-result');
      F.close(); await sleep(200);
      res.closed = !document.querySelector('#fxOv');
      return res;
    });
    // 第5弾：特別な 演出（16.3）。プレミアムど的中（部品 約1800・落ちない・絵は 手元の ios/fx_assets/ から → CIでは 404 でも 流れは 動く）・
    // 超神様的中（動画は リポジトリに 入れない → CIでは 読めない → さいごの 1まい → 1.3秒で ボード）。第4.86版：神様的中・超プレミアムど的中・隠れど的中は なし
    await step(R, 'fx5', async function () {
      var F = window.TengelFx; if (!F) return { on: false };
      var spec = { r: 8, n: 14, rows: [{ t: '3連単', state: '的中', hits: [[11, 8, 2]], n: 18 }, { t: '馬単', state: '的中', hits: [[11, 8]], n: 9 }], ranks: { 11: 11, 8: 8, 2: 2 } };
      function fps(ms) { return new Promise(function (r) { var n = 0, t0 = performance.now(); (function tick() { n++; if (performance.now() - t0 < ms) requestAnimationFrame(tick); else r(Math.round(n * 1000 / ms)); })(); }); }
      function closeVis() { var c = document.querySelector('#fxOv .close'); return c ? getComputedStyle(c).visibility : null; }
      var res = { decide: F.decide(spec), lottery: [F.lottery('fz'), F.lottery('gd')], films: Object.keys(window.__FX.films || {}), assets: {} };
      for (var k of ['pm_face_F.webp', 'sgd_film.mp4', 'sgd_last.webp', 'sfx_pc.m4a']) { try { var r = await fetch(k, { cache: 'no-store' }); res.assets[k] = r.status; } catch (e) { res.assets[k] = String(e); } }
      res.gone = { reveal: ['hidden', 'zp', 'gd'].filter(function (k) { return !!(window.__FX.reveal || {})[k]; }), art: !!(window.__FX.art || {}).gd, sfx: !!(window.__FX.sfx || {}).gd };   // 第4.86版：消した 演出は 入って いない
      // プレミアムど的中（ハートの 雨 → ポニー ①〜⑤（1つ 1.0秒）→ ハートの 地面に ど的中が 落ちて 刺さる → ボード：10.07秒・第4.86版）
      res.pc = { kind: F.show(Object.assign({ force: 'pc' }, spec, { ranks: { 11: 11, 8: 6, 2: 2 } })), push: !!document.querySelector('#fxOv .ov.fz .pbox.rbw .push .rbf') };
      await sleep(400); F.tap(); var pcT = Date.now(); res.pc.fps = await fps(1000);
      res.pc.parts = ['.pmbg', '.pmp', '.pms', '.pmf', '.pmw', '.pmfj', '.pmhz', '.pmhp', '.pmsp'].map(function (c) { return document.querySelectorAll('#fxOv .ov.pm ' + c).length; });
      await sleep(3200); res.pc.fps4 = await fps(1000);   // ポニーの ① の ころ
      await mark('fx-pc');
      // 第4.80版：ハートの 地面が できて、ゼリーの ハートが 上から 落ちて 先が 地面に 着いて 1/3 うまる → ぷるんぷるん → 上へ（第4.86版：8.55秒に 着いて 9.95秒に 上へ）→ 9.5秒ごろを 写す
      await sleep(Math.max(0, 9500 - (Date.now() - pcT)));
      var pmf = document.querySelector('#fxOv .ov.pm .pmf');
      res.pc.land = { t: Date.now() - pcT, tf: pmf ? getComputedStyle(pmf).transform : null, heap: document.querySelectorAll('#fxOv .ov.pm .pmhp > i').length };
      await mark('fx-pc-land');
      await waitFor(function () { return closeVis() === 'visible'; }, 16000);
      res.pc.title = (document.querySelector('#fxOv .rb .bh') || {}).innerText || null; res.pc.closeVis = closeVis();
      await mark('fx-pc-board');
      F.close(); await sleep(300);
      // 超神様的中（動画が ない → still）
      res.sgd = { kind: F.show(Object.assign({ force: 'sgd' }, spec)), push: !!document.querySelector('#fxOv .ov.fz .pbox.rbw .push .rbf') };
      await sleep(400); F.prime(); F.tap(); await sleep(400);
      res.sgd.cur = F.current(); res.sgd.ov = (document.querySelector('#fxOv .ov.sgd') || {}).className || null; res.sgd.video = !!document.querySelector('#fxOv video');
      await waitFor(function () { return closeVis() === 'visible'; }, 8000);
      res.sgd.title = (document.querySelector('#fxOv .rb .bh') || {}).innerText || null; res.sgd.closeVis = closeVis(); res.sgd.holder = document.querySelectorAll('#fxVh video').length;
      await mark('fx-sgd-still');
      F.close(); await sleep(200);
      // 第4.66版〜：ど的中・紫電（第4.71版：押した 瞬間に プチュン → 動画 sd_film.mp4（暗闇に 光る 目と 馬の 顔 → 縦書きの 的中を 蹄が 切り裂く → 3D の ど！！！的中）→ ボード 10.05秒）。
      // 動画は リポジトリに 入れない → CIでは 読めない → 動画の さいごの 1まい（still：プチュンは 出さない）→ 1.3秒で ボード。PUSH は ど的中と 同じ（虹色なし・1.4倍）
      res.sd = { kind: F.show(Object.assign({ force: 'sd' }, spec, { ranks: { 11: 11, 8: 6, 2: 2 } })), push: !!document.querySelector('#fxOv .ov.fz .pbox.pz .push'), rbw: !!document.querySelector('#fxOv .ov.fz .pbox.rbw'), pz: (F.current() || {}).pz };
      await sleep(400); F.prime(); F.tap(); res.sd.fps = await fps(1000);
      // 第4.77版：極ど的中（紫電）は ノーマルど的中の 動画から 入る（CIでは 動画が ない → すぐ 極ど的中 → still）
      res.sd.pre0 = (F.current() || {}).pre; res.sd.nd0 = !!document.querySelector('#fxOv .ov.nd');
      await waitFor(function () { return (F.current() || {}).film === 2; }, 12000);
      res.sd.parts = ['.sds', '.sdk', '.pc', '.hb'].map(function (c) { return document.querySelectorAll('#fxOv .ov.sd ' + c).length; });
      res.sd.imgs = document.querySelectorAll('#fxOv .ov.sd img').length; res.sd.broken = Array.prototype.filter.call(document.querySelectorAll('#fxOv .ov.sd img'), function (i) { return i.complete && i.naturalWidth === 0; }).length;
      res.sd.cur = F.current(); res.sd.ov = (document.querySelector('#fxOv .ov.sd') || {}).className || null; res.sd.nd = !!document.querySelector('#fxOv .ov.nd');
      res.sd.holder = !!document.querySelector('#fxVh video[data-film=sd_film]') && !!document.querySelector('#fxVh video[data-film=nd_film]');
      await mark('fx-sd');                                         // 動画の さいごの 1まい（still）
      await waitFor(function () { return closeVis() === 'visible'; }, 8000);
      res.sd.title = (document.querySelector('#fxOv .rb .bh') || {}).innerText || null; res.sd.rib = (document.querySelector('#fxOv .rb .zrib') || {}).innerText || null; res.sd.closeVis = closeVis();
      await mark('fx-sd-board');
      F.close(); await sleep(200);
      // 第4.77版：ノーマルど的中（nd：押すと 1秒 真っ暗（プチュンは なし）→ 動画 nd_film.mp4（光の 玉 → シルバーの 競走馬と 騎手 → 芝に 落ちる 3D の ど！的中）→ ボード 10.05秒）。
      // 動画は リポジトリに 入れない → CIでは 読めない → 動画の さいごの 1まい（still）→ 1.3秒で ボード。PUSH は ど的中と 同じ（虹色なし・1.4倍）
      res.nd = { kind: F.show(Object.assign({ force: 'nd' }, spec, { ranks: { 11: 11, 8: 6, 2: 2 } })), push: !!document.querySelector('#fxOv .ov.fz .pbox.pz .push'), rbw: !!document.querySelector('#fxOv .ov.fz .pbox.rbw'), pz: (F.current() || {}).pz };
      await sleep(400); F.prime(); F.tap(); res.nd.fps = await fps(1000);
      res.nd.parts = ['.nds', '.ndk', '.pc', '.hb'].map(function (c) { return document.querySelectorAll('#fxOv .ov.nd ' + c).length; });
      res.nd.imgs = document.querySelectorAll('#fxOv .ov.nd img').length; res.nd.broken = Array.prototype.filter.call(document.querySelectorAll('#fxOv .ov.nd img'), function (i) { return i.complete && i.naturalWidth === 0; }).length;
      await waitFor(function () { return (F.current() || {}).film === 2; }, 6000);
      res.nd.cur = F.current(); res.nd.ov = (document.querySelector('#fxOv .ov.nd') || {}).className || null; res.nd.holder = !!document.querySelector('#fxVh video[data-film=nd_film]');
      res.nd.ndt = !!document.querySelector('#fxOv .ov.nd .ndt .pressed'); await sleep(1200);   // 第4.79版：押した 画面（PUSH の 画面とは 別）は 約1秒で 消える
      res.nd.ndtGone = getComputedStyle(document.querySelector('#fxOv .ov.nd .ndt')).visibility === 'hidden';
      await mark('fx-nd');                                         // 動画の さいごの 1まい（still）
      await waitFor(function () { return closeVis() === 'visible'; }, 8000);
      res.nd.title = (document.querySelector('#fxOv .rb .bh') || {}).innerText || null; res.nd.rib = (document.querySelector('#fxOv .rb .zrib') || {}).innerText || null; res.nd.closeVis = closeVis();
      await mark('fx-nd-board');
      F.close(); await sleep(200);
      res.closed = !document.querySelector('#fxOv');
      return res;
    });
    // 第4弾：着せ替え。テーマを 切り替えて（解放の 確認は test_native）判定タブの 上の絵・色・字・テーマの 的中PUSH と ボードを 確かめる。
    // 見本の絵（ks_<id>.webp）は リポジトリに 入れないので、CIでは 404（なしでも 動く ことを 確かめる）。字（ks の WOFF2）と ks_<id>.json は 入っている
    await step(R, 'kisekae', async function () {
      var K = window.TengelKisekae; if (!K) return { on: false };
      await K.ready;
      var res = { list: K.list().length, groups: Array.from(new Set(K.list().map(function (t) { return t.group; }))), current0: K.current(), count: K.count(), usableSakura: K.usable('sakura'), band: K.band, files: {} };
      for (var k of ['ks_sakura.json', 'ks_banner_ranch.svg', 'fonts/KaiseiDecol-700.woff2', 'ks_cbcbaeebec4470155b1587d5a5c8fe00.webp']) { try { var r = await fetch(k, { cache: 'no-store' }); res.files[k] = r.status; } catch (e) { res.files[k] = String(e); } }
      await K.apply('sakura'); await sleep(900);
      document.querySelector('.tabbar [data-tab=judge]').click(); await sleep(400);
      var bn = document.querySelector('#ksBnr');
      res.sakura = { ks: document.documentElement.dataset.ks, loaded: K.loaded(), bnr: bn ? { hidden: bn.hidden, h: bn.getBoundingClientRect().height, w: bn.getBoundingClientRect().width, k: bn.style.getPropertyValue('--ksk'), anims: bn.getAnimations({ subtree: true }).length, inner: !!bn.querySelector('.bnrw') } : null,
        bg: getComputedStyle(document.body).backgroundColor, font: getComputedStyle(document.body).fontFamily.slice(0, 40), hfont: getComputedStyle(document.querySelector('.brand h1')).fontFamily.slice(0, 30),
        fontLoaded: document.fonts.check('700 16px "Kaisei Decol"'), themeCss: !!document.querySelector('#ksTheme') && document.querySelector('#ksTheme').textContent.length, scrollW: document.documentElement.scrollWidth };
      await mark('ks-judge');
      var F = window.TengelFx;
      F.show({ r: 8, n: 14, rows: [{ t: '馬単', state: '的中', hits: [[6, 2]], n: 9 }, { t: '単勝', state: '的中', hits: [[6]], n: 3 }], ranks: { 6: 1, 2: 2 }, force: 'hit' }); await sleep(600);
      res.push = { cls: (document.querySelector('#fxOv .push') || {}).className, svg: !!document.querySelector('#fxOv .push svg'), theme: (F.current() || {}).theme };
      await mark('ks-push');
      F.tap(); await waitFor(function () { var c = document.querySelector('#fxOv .close'); return c && getComputedStyle(c).visibility === 'visible'; }, 6000);
      var rb = document.querySelector('#fxOv .rb');
      res.board = rb ? { cls: rb.className, title: rb.querySelector('.bh').innerText, orn: !!rb.querySelector('.orn'), pressed: (document.querySelector('#fxOv .pressed') || {}).className } : null;
      await mark('ks-board');
      F.close(); await sleep(200);
      document.querySelector('.tabbar [data-tab=set]').click(); await sleep(400);
      var card = document.querySelector('#setKisekae');
      if (card) { card.scrollIntoView({ block: 'start' }); await sleep(300); }
      res.card = card ? { tiles: card.querySelectorAll('.kst').length, on: (card.querySelector('.kst.on') || {}).dataset ? card.querySelector('.kst.on').dataset.ks : null, locks: card.querySelectorAll('.kst.lock').length, names: Array.from(card.querySelectorAll('.kst .ksn')).slice(0, 6).map(function (e) { return e.innerText; }) } : null;
      await mark('ks-set');
      // 第4.64版：カギの 壁紙を タップ → その タイルの 中（カギの 下）に 確認（「○Pを使って解放する？」「解放する」「やめる」）。一覧の 上の 帯は ない。もう一度 タップで 閉じる
      var lk = card && card.querySelector('.kst.lock[data-ks=lucky]');
      if (lk) {
        lk.click(); await sleep(400);
        var cf = card.querySelector('.kst.cf .ksconf'), un = cf && (cf.querySelector('[data-ksact=unlock]') || cf.querySelector('.btn')), lkb = card.querySelector('.kst[data-ks=lucky] .kslock');   // P が 足りない ときは「ポイントを買う」で 測る
        lk = card.querySelector('.kst[data-ks=lucky]') || lk;                                                                    // paint() で タイルは 作り直されるので、測る 前に さがし直す
        res.conf = { tile: (card.querySelector('.kst.cf') || {}).dataset ? card.querySelector('.kst.cf').dataset.ks : null, role: lk.getAttribute('role'), text: cf ? cf.innerText.replace(/\n/g, '／') : null,
          unlock: !!(cf && cf.querySelector('[data-ksact=unlock]')), buy: !!(cf && cf.querySelector('[data-gopt=points]')), cancel: !!(cf && cf.querySelector('[data-ksact=cancel]')), top: !!card.querySelector('.ksbody > .ksconf'),
          below: !!(un && lkb && un.getBoundingClientRect().top >= lkb.getBoundingClientRect().bottom - 1), inside: !!(un && un.getBoundingClientRect().right <= lk.getBoundingClientRect().right + 1 && un.getBoundingClientRect().bottom <= lk.getBoundingClientRect().bottom + 1) };
        var lk2 = card.querySelector('.kst.cf') || lk;                      // paint() で タイルは 作り直されるので、もう一度 さがす
        lk2.scrollIntoView({ block: 'center' }); await sleep(300);
        await mark('ks-conf');
        lk2.click(); await sleep(300);
        res.conf.closed = !card.querySelector('.ksconf');
      } else { res.conf = null; await mark('ks-conf'); }
      await K.apply('tengel'); await sleep(900);
      document.querySelector('.tabbar [data-tab=judge]').click(); await sleep(400);
      res.tengel = { ks: document.documentElement.dataset.ks, bg: getComputedStyle(document.body).backgroundColor, anims: (document.querySelector('#ksBnr') || { getAnimations: function () { return []; } }).getAnimations({ subtree: true }).length, scrollW: document.documentElement.scrollWidth };
      await mark('ks-tengel');
      await K.apply('default'); await sleep(400);
      res.back = { ks: document.documentElement.dataset.ks || null, bnrHidden: (document.querySelector('#ksBnr') || {}).hidden };
      return res;
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
    await step(R, 'wallet2', wallet);
    // App内課金：商品（シミュレーターでは App Store Connect の設定がないので、読めないことが多い。読めなくてもアプリは動く）
    await step(R, 'iap', async function () { return await TengelNative.iap('products'); });
    await step(R, 'layout', async function () { var L = await TengelNative.layout(); L.cssTop = getComputedStyle(document.documentElement).getPropertyValue('--top-inset'); L.cssBottom = getComputedStyle(document.documentElement).getPropertyValue('--bottom-inset'); L.padTop = getComputedStyle(document.documentElement).paddingTop; L.padBottom = getComputedStyle(document.documentElement).paddingBottom; return L; });
    // 第4.59版：上の帯の 所有ポイント（購入・サブスク）・説明書は マザーデータの 札の すぐ 左・iPad で 画面いっぱいなら 上に 24px（互換モードでは つかない）
    await step(R, 'topbar', function () {
      var p = document.querySelector('#ptsPill'), m = document.querySelector('#manBtn'), d = document.querySelector('#dbpill'), h = document.querySelector('header.top');
      var r = function (x) { return x ? x.getBoundingClientRect() : null; };
      return { pill: p ? p.innerText.replace(/\s+/g, ' ') : null, manual: m ? { right: r(m).right, top: r(m).top } : null, badge: d ? { left: r(d).left, right: r(d).right, top: r(d).top } : null,
               headerTop: h ? r(h).top : null, topInset: document.documentElement.style.getPropertyValue('--top-inset'), topInset2: document.documentElement.style.getPropertyValue('--top-inset2'), w: innerWidth, test: !!window.__TEST, testTag: !!document.querySelector('#testTag') };
    });
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
    var ptc = document.querySelector('#setPoints'); if (ptc) { ptc.scrollIntoView({ block: 'start' }); await sleep(500); await mark('points'); }
    R.settings = { points: ptc ? ptc.innerText.slice(0, 600) : null, custom: (document.querySelector('#setCustom') || {}).innerText || null, mission: (document.querySelector('#setMission') || {}).innerText || null, update: up ? up.innerText : null, data: (document.querySelector('#setData') || {}).innerText || null };
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
    // CM の カードは App Store版の 設定には ない（2026/10/25）
    R.cm = { card: !!document.querySelector('#setCM'), modal: !!document.querySelector('#cmModal') };
    // 記録タブ
    tab('rec'); await sleep(900); window.scrollTo(0, 0); await sleep(300);
    await mark('rec');
    // 第4.62版：テンキー（数字の 欄に 入って 0.65秒 キーボードが 出なければ 出る。スクリプトの focus() では キーボードは 出ないので、ここでは 出る はず）
    await step(R, 'numpad', async function () {
      tab('win5'); await sleep(800);
      var f = document.querySelector('#w5Win0');
      if (!f || !window.TengelNumpad) return { field: !!f, numpad: !!window.TengelNumpad };
      f.scrollIntoView({ block: 'center' }); await sleep(300); f.focus(); await sleep(1100);
      var s1 = TengelNumpad.state(), out = { shown: s1.open, target: s1.target, vh: s1.vh, base: s1.base, hw: s1.hw, kb: s1.kb, active: document.activeElement.id };
      var b = document.querySelector('#numPad button[data-k="7"]'); if (b) b.click(); await sleep(150);
      out.value = f.value; out.activeAfter = document.activeElement.id;
      var np = document.querySelector('#numPad'); if (np) { var r = np.getBoundingClientRect(); out.box = { top: Math.round(r.top), h: Math.round(r.height), bottom: Math.round(innerHeight - r.bottom) }; }
      await mark('numpad');
      var d = document.querySelector('#numPad button[data-k="done"]'); if (d) d.click(); await sleep(250);
      out.closed = !TengelNumpad.state().open; out.activeDone = document.activeElement.tagName;
      setVal(f, '');
      return out;
    });
    // 第4.62版：説明書は アプリの 中の 重ねた 窓（iframe）で 開く：ページは そのまま・「アプリに戻る」で 窓が 閉じる
    await step(R, 'manualOv', async function () {
      tab('rec'); await sleep(600);
      var b = document.querySelector('#manBtn'); if (!b || !window.TengelManual) return { btn: !!b, api: !!window.TengelManual };
      var href0 = location.href; b.click();
      var fr = await waitFor(function () { var f = document.querySelector('#manOv iframe'); return f && f.contentDocument && f.contentDocument.readyState === 'complete' && f.contentDocument.querySelector('#home') ? f : null; }, 10000);
      var out = { overlay: !!document.querySelector('#manOv'), loaded: !!fr, href: location.href, same: location.href === href0 };
      if (!fr) { await mark('manual-ov'); await mark('manual-ov-item'); TengelManual.close(); return out; }
      await sleep(1200);
      var doc = fr.contentDocument, imgs = Array.prototype.slice.call(doc.images);
      out.src = fr.src; out.title = doc.title; out.imgs = imgs.length; out.loaded = imgs.filter(function (i) { return i.complete && i.naturalWidth > 0; }).length;
      var sel = document.querySelector('.tabbar [aria-selected=true]'); out.tab = sel ? sel.dataset.tab : null;
      await mark('manual-ov');
      var row = doc.querySelector('.mrow'); if (row) { row.click(); await sleep(900); out.item = { hash: doc.location.hash, page: !(doc.querySelector('#page') || { hidden: true }).hidden, close: !!doc.querySelector('#closeApp:not([hidden])') }; }
      await mark('manual-ov-item');
      var c = doc.querySelector('#closeApp:not([hidden])') || doc.querySelector('#toApp'); if (c) c.click(); await sleep(800);
      out.closed = !document.querySelector('#manOv'); out.hrefAfter = location.href; out.gate = !!document.querySelector('#gateGo'); out.scroll = document.documentElement.classList.contains('manon');
      var sel2 = document.querySelector('.tabbar [aria-selected=true]'); out.tabAfter = sel2 ? sel2.dataset.tab : null;
      if (!out.closed) TengelManual.close();
      return out;
    });
    // 外への通信（Google のフォントなどがないか）
    R.outside = performance.getEntriesByType('resource').map(function (e) { return e.name; }).filter(function (n) { return !/^tengel:/.test(n); });
    report('1', R);
    await sleep(500);
    sessionStorage.setItem('st1', 'done'); sessionStorage.setItem('st1done', '1');
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
    await step(R, 'wallet', wallet);
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
    await step(R, 'walletBefore', wallet);   // 保存場所を消したあと：初回の1,500Pはもう出ない（キーチェーンのしるし）
    await mark('offer');
    var yes = document.querySelector('#nativeRestore [data-nr=yes]'); if (yes) yes.click();
    await waitFor(function () { return TengelLocal.mem.bets.size > 0; }, 10000);
    await sleep(800);
    R.after = { bets: TengelLocal.mem.bets.size, ids: Array.from(TengelLocal.mem.bets.keys()), toast: (document.querySelector('#toast') || {}).textContent, offer: !!document.querySelector('#nativeRestore') };
    await step(R, 'walletAfter', wallet);   // 戻すと台帳も戻る
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
