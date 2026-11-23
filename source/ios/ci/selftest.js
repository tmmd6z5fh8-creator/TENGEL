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
// 4回目（第4.156版）：iPad の 広い 窓（run.sh が .pad を 足して 作った アプリ＝Swift Playgrounds の ▶ と 同じ 形）で、アプリが iPhone の 大きさ（390×844）で まん中に 出るか
// 6回目・7回目（第4.176版）：馬カードバトルの「部屋」を 本物の アプリ（Room.swift＝MultipeerConnectivity）で。run.sh が iPhone と iPad の シミュレーターを 同時に 起こして、
//        iPhone＝部屋を 作る（6回目）・iPad＝部屋に 入る（7回目）。部屋番号は run.sh が window.__ST_ROOM で 渡す。つながったら 2台とも 自動で さいごまで 対戦して 結果を 書く
//        （1回目にも コンピュータとの 対戦を 入れた：本物の WebKit で 入口・本体・対戦・アプリの 部屋の 窓口の 返事を 見る）
// 5回目（第4.169版）：テスト版の「ぜんぶ リセット」（reset_all.js）を 本物の WKWebView で。出す アプリには 消す しかけが 入って いない ので、
//        run.sh が この ファイルの 先頭に「window.__TEST = true;」と reset_all.js を 足す（＝テスト版と 同じ 形：ほかの どの コードより 先に 動く）
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
  // 第4.191版：時計の 番人（アプリの 時計 Clock.swift：wall・mono〈電源を 入れてからの 時間〉・boot・proc・dev／Webの 画面の TengelClock）
  async function clock() {
    var t0 = Date.now(), a = await TengelNative.call('clock', {}).catch(function (e) { return { error: String(e) }; }), t1 = Date.now();
    await sleep(400);
    var b = await TengelNative.call('clock', {}).catch(function (e) { return { error: String(e) }; });
    // 第4.212版：インターネットの 時刻（Clock.swift の net：App Store の lookup の 返事の 日付）。net.t は 聞いた ときの 時刻・rt は 行って 帰る までの 時間
    // 第4.213版：GitHub の Mac の 通信が 一瞬 切れる ことが ある（run 183 の macOS 26：2回目の 起動で 1回 通らなかった）→ 通らなかった（why＝net）とき だけ、2秒 あけて 2回まで 聞き直す。
    //   何回目で 通ったかを 報告に のこす（netTries）。3回とも 通らなければ CHECK の まま（本当に つながらない）
    var n = null, tries = 0;
    for (;;) {
      n = await TengelNative.call('clock', { net: 1 }).catch(function (e) { return { error: String(e) }; }); tries++;
      if (tries >= 3 || !(n && n.net && n.net.ok === false && n.net.why === 'net')) break;
      await sleep(2000);
    }
    var tn = Date.now();
    var C = window.TengelClock; if (C) await C.sync();
    return { a: a, b: b, js: [t0, t1], has: !!C, how: C ? C.how() : null, st: C ? C.state() : null, diff: C ? Math.round(C.now() - Date.now()) : null,
      net: n && n.net ? n.net : (n && n.error ? { error: n.error } : null), netDiff: n && n.net && n.net.ok ? Math.round(n.net.t - tn) : null, netTries: tries, sure: C && typeof C.sure === 'function' ? C.sure() : null };
  }
  // 第4.212版：おもちゃ（TENGERカードバトル・お世話チャレンジ：1つ 3,000P で 解放）を 0P で 解放した ことに する（台帳に しるしを 足して 入れ直す：アプリの 自動バックアップから 戻す 口と 同じ。
  //   シミュレーターは キーチェーンが 使えなくて 初回プレゼントが 入らない ことが ある ので、ポイントは 使わない）
  async function openToys(ids) {
    var W = window.TengelWallet; if (!W || !W.toy) return null;
    await W.ready;
    var s = W.snapshot(); if (!s) return null;
    var n = 0, add = 0; s.events.forEach(function (ev) { if (ev && +ev.n > n) n = +ev.n; });
    ids.forEach(function (id) {
      if (s.events.some(function (ev) { return ev && ev.id === 'unlock-toy:' + id; })) return;
      s.events.push({ id: 'unlock-toy:' + id, kind: 'unlock', bucket: '', amount: 0, at: new Date().toISOString(), what: 'toy:' + id, device: 'selftest', use: { paid_sub: 0, paid_pack: 0, free: 0 }, n: ++n }); add++;
    });
    if (add) { await W.restore(s); document.dispatchEvent(new CustomEvent('tengel:wallet')); }
    return ids.map(function (id) { return W.toy.has(id); });
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
    await step(R, 'clock', clock);      // 第4.191版
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
    // 第4.122版：上の帯の「結果待ち」（予約した レースの 数）→ 押すと 窓（ゾーンごとの 1着・2着・3着の 馬・点数）→ とじる
    await step(R, 'rsvList', async function () {
      var b = document.querySelector('#rsvBtn'); if (!b) return { btn: false };
      await waitFor(function () { return /結果待ち\s*1/.test(b.innerText); }, 5000);
      var t = b.innerText.replace(/\s+/g, ''); b.click(); await sleep(600);
      var ov = document.querySelector('#rsvOv');
      return { btn: t, ov: !!ov, cards: ov ? ov.querySelectorAll('.rvcard').length : 0, legs: ov ? ov.querySelectorAll('.rvleg').length : 0, text: ov ? ov.innerText.slice(0, 160) : '' };
    });
    await mark('rsv-ov');
    var rvc = document.querySelector('#rsvOv [data-rv=close]'); if (rvc) { rvc.click(); await sleep(300); }
    // 第3弾：的中ボタン。CIの保存は予約まで（結果は入れない）なので、演出を直接出して確かめる：デカ的中の PUSH → タップ → いつものボード／ど的中の PUSH → 結果の画面。
    // 絵と音のファイル（sfx_*.m4a など）はリポジトリに入れないので、CIでは 404（なしでも動くことを確かめる）。
    // 第4.109版：前の ど的中（fz：フリーズ・ネオンの カット）は アプリに 入れて いない → force:'fz' は ノーマルど的中（nd）に なる（PUSH と ボードは ど的中の 形）
    // 第4.165版：ノーマルど的中は なくした → force:'fz' は 極ど的中（sd）に なる（PUSH は 同じ 1.4倍・動画が ない CI では さいごの 1まい → ボード）
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
      for (var k of ['sfx_fz_push.m4a', 'sfx_big.m4a']) { try { var r = await fetch(k, { cache: 'no-store' }); res.assets[k] = r.status; } catch (e) { res.assets[k] = String(e); } }
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
      // 第4.124版：force:'fz' は ノーマルど的中（.ov.nd・第4.165版から 極ど的中 .ov.sd）に なる → .ov.fz が なくても 止まらない ように（前は getComputedStyle(null) で ここで 止まり、印 fx-fz-result が 出なかった）
      var q1 = function (s) { return document.querySelector(s); }, cs1 = function (s, k) { var e = q1(s); return e ? getComputedStyle(e)[k] : null; };
      res.fz = { ov: (q1('#fxOv .ov') || {}).className || null, rib: (q1('#fxOv .rb .zrib') || {}).innerText || null, title: (q1('#fxOv .rb .bh') || {}).innerText || null, closeVis: cs1('#fxOv .close', 'visibility'), finOpacity: cs1('#fxOv .ov .fin', 'opacity') };
      await mark('fx-fz-result');
      F.close(); await sleep(200);
      res.closed = !document.querySelector('#fxOv');
      return res;
    });
    // 第5弾：特別な 演出（16.3）。超神様的中（動画は リポジトリに 入れない → CIでは 読めない → さいごの 1まい → 1.3秒で ボード）。第4.86版：神様的中・超プレミアムど的中・隠れど的中は なし
    // 第4.162版（まさちゃん 2026/11/12 22:56「プレミアムど的中／超プレミアム神様的中／この二つ消して！」）：プレミアムど的中・超プレミアム神様的中も なし
    //   （押したあと・絵・音・昇格の 動画は 束に ない・くじも ない。決めて 出す とき（force）は プレミアムど的中 → ノーマルど的中・超プレミアム神様的中 → 超神様的中）
    await step(R, 'fx5', async function () {
      var F = window.TengelFx; if (!F) return { on: false };
      var spec = { r: 8, n: 14, rows: [{ t: '3連単', state: '的中', hits: [[11, 8, 2]], n: 18 }, { t: '馬単', state: '的中', hits: [[11, 8]], n: 9 }], ranks: { 11: 11, 8: 8, 2: 2 } };
      function fps(ms) { return new Promise(function (r) { var n = 0, t0 = performance.now(); (function tick() { n++; if (performance.now() - t0 < ms) requestAnimationFrame(tick); else r(Math.round(n * 1000 / ms)); })(); }); }
      function closeVis() { var c = document.querySelector('#fxOv .close'); return c ? getComputedStyle(c).visibility : null; }
      var A = window.__FX || {};
      var res = { decide: F.decide(spec), lottery: typeof F.lottery, films: Object.keys(A.films || {}), assets: {} };   // 第4.162版：くじは ない（F.lottery も ない）
      for (var k of [(A.films || {}).sgd_film, ((A.art || {}).sgd || [])[0], (A.sfx || {}).sgd]) { try { var r = await fetch(k, { cache: 'no-store' }); res.assets[k] = r.status; } catch (e) { res.assets[k] = String(e); } }
      // 第4.86版・第4.162版：消した 演出は 入って いない（押したあと・絵・音・昇格の 動画）。決めて 出すと ノーマルど的中・超神様的中に なる
      res.gone = { reveal: ['hidden', 'zp', 'gd', 'pc', 'spg'].filter(function (k) { return !!(A.reveal || {})[k]; }), art: ['gd', 'pm'].filter(function (k) { return !!(A.art || {})[k]; }),
        sfx: ['gd', 'pc', 'zp', 'spg', 'spg_up'].filter(function (k) { return !!(A.sfx || {})[k]; }), films: !!(A.films || {}).spg_up, force: [] };
      for (var fk of ['pc', 'spg']) { res.gone.force.push(F.show(Object.assign({ force: fk }, spec)) + '/' + ((F.current() || {}).kind || '')); await sleep(200); F.close(); await sleep(200); }
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
      // 第4.165版（まさちゃん 2026/11/13 11:52「あと、ノーマル的中の演出消して！」）：ノーマルど的中は なし。決めて 出す とき（force:'nd'）も、D で M で ない 当たり（decide）も 極ど的中（sd）に なる。
      // 極ど的中の 入り（ノーマルど的中の 幕と 動画の はじめ）は そのまま（上の res.sd）。前は ここで ノーマルど的中の 流れ（押した 画面 → さいごの 1まい → ボード）を 見て いた
      res.nd = { kind: F.show(Object.assign({ force: 'nd' }, spec, { ranks: { 11: 11, 8: 6, 2: 2 } })), cur: (F.current() || {}).kind, push: !!document.querySelector('#fxOv .ov.fz .pbox.pz .push'), pz: (F.current() || {}).pz,
        decide: F.decide(Object.assign({}, spec, { ranks: { 11: 11, 8: 6, 2: 2 } })).kind };
      await sleep(300); F.close(); await sleep(200);
      // 第4.117版：神様極的中（gk：超神様と 同じ 虹色の PUSH（1.6倍）→ 押した 画面（ノーマルど的中と 同じ）→ 動画 gk_film.mp4（12.03秒）→ ボード 12.0秒）。
      // 動画は リポジトリに 入れない → CIでは 読めない → 動画の さいごの 1まい（still）→ 1.3秒で ボード「神様極的中！！！」（帯は 超大穴と 大穴）
      res.gk = { kind: F.show(Object.assign({ force: 'gk' }, spec)), push: !!document.querySelector('#fxOv .ov.fz .pbox.rbw .push .rbf'), pz: (F.current() || {}).pz };
      await sleep(400); F.prime(); F.tap(); res.gk.fps = await fps(1000);
      res.gk.parts = ['.gks', '.gkk', '.ndt', '.hb'].map(function (c) { return document.querySelectorAll('#fxOv .ov.gk ' + c).length; });
      res.gk.imgs = document.querySelectorAll('#fxOv .ov.gk img').length; res.gk.broken = Array.prototype.filter.call(document.querySelectorAll('#fxOv .ov.gk img'), function (i) { return i.complete && i.naturalWidth === 0; }).length;
      await waitFor(function () { return (F.current() || {}).film === 2; }, 6000);
      res.gk.cur = F.current(); res.gk.ov = (document.querySelector('#fxOv .ov.gk') || {}).className || null; res.gk.holder = !!document.querySelector('#fxVh video[data-film=gk_film]');
      res.gk.ndtGone = (function (e) { if (!e) return null; var c = getComputedStyle(e); return c.visibility === 'hidden' || c.display === 'none'; })(document.querySelector('#fxOv .ov.gk .ndt'));   // 第4.124版：ない ときも 止まらない
      await mark('fx-gk');                                         // 動画の さいごの 1まい（still）
      await waitFor(function () { return closeVis() === 'visible'; }, 8000);
      res.gk.title = (document.querySelector('#fxOv .rb .bh') || {}).innerText || null; res.gk.rib = (document.querySelector('#fxOv .rb .zrib') || {}).innerText || null; res.gk.closeVis = closeVis();
      await mark('fx-gk-board');
      F.close(); await sleep(200);
      res.closed = !document.querySelector('#fxOv');
      return res;
    });
    // 第4.91版：結果ボードカスタム（買い切り）。シミュレーターでは App内課金の 商品が 読めない ことが 多いので、買わずに 設定の「▶ 見る」と 同じ ためしで 飾りを 出す。
    // 第4.113版：16「ボードを持つ馬」（的中・ハズレの ボードの 両方。登場 1秒 → 1.5秒後に 1回 落としそうに なる）。絵（bcx_hb_*.webp）が ない ときは SVG の 馬
    await step(R, 'board', async function () {
      var T = window.TengelBoard, F = window.TengelFx, Wl = window.TengelWallet; if (!T || !F) return { on: false };
      var spec = { r: 8, n: 14, rows: [{ t: '3連単', state: '的中', hits: [[11, 8, 2]], n: 18 }, { t: '馬単', state: '的中', hits: [[11, 8]], n: 9 }], ranks: { 11: 11, 8: 8, 2: 2 } };
      var res = { items: T.items().length, info: Wl && Wl.board ? Wl.board.info() : null, card: !!document.querySelector('#setBoard'), tiles: document.querySelectorAll('#setBoard .bct').length, buy: (document.querySelector('#setBoard [data-bcact=buy]') || {}).innerText || null };
      res.ready = T.items().filter(function (i) { return i.ready; }).map(function (i) { return i.id; });
      if (res.info) { delete res.info.items; delete res.info.need; }
      F.preview(spec, 'hit', { item: 'carry' }); await sleep(2600);
      var hb = document.querySelector('#fxOv .hb'), c = document.querySelector('#fxOv .close');
      res.carry = hb ? { bcx: hb.dataset.bcx || '', cls: hb.className, parts: hb.querySelectorAll('.bcx').length, vec: hb.classList.contains('bchbv'), close: c ? Math.round(c.getBoundingClientRect().top) : null } : null;
      await mark('board-carry');
      await sleep(1000);
      await mark('board-carry-slip');
      F.close(); await sleep(300);
      var miss = { r: 8, n: 14, rows: [{ t: '3連単', state: '不的中', hits: [], n: 18 }, { t: '馬単', state: '不的中', hits: [], n: 9 }], ranks: { 11: 11, 8: 8, 2: 2 } };
      F.preview(miss, 'miss', { item: 'carry' }); await sleep(2600);
      hb = document.querySelector('#fxOv .hb');
      res.carryMiss = hb ? { bcx: hb.dataset.bcx || '', kind: (F.current() || {}).kind || null } : null;
      await mark('board-carry-miss');
      F.close(); await sleep(200);
      // 第4.121版：絵の ボード（デザインの 絵）。CI には 絵が ない ので、読めない とき いつもの ボードに もどる（.bcpic なし・ボードは .hb の 中）ことを 見る
      //   第4.214版：絵の ボードは 11こ（「結果ボードを廻る」〈ring〉は 消した）→「馬達の祝杯」（toast）で 見る
      F.preview(spec, 'hit', { item: 'toast', streak: 2 }); await sleep(2600);
      hb = document.querySelector('#fxOv .hb');
      res.pic = hb ? { bcx: hb.dataset.bcx || '', bcp: hb.dataset.bcp || '', pic: hb.classList.contains('bcpic'), rbInHb: !!(hb.querySelector('.rb') && hb.querySelector('.rb').parentNode === hb),
        stage: T.stage ? T.stage('toast', 2) : null, n: Object.keys((window.__BCP && window.__BCP.items) || {}).length } : null;
      F.close(); await sleep(200);
      F.preview(miss, 'miss', { item: 'rain', streak: 9 }); await sleep(2000);
      hb = document.querySelector('#fxOv .hb');
      res.picMiss = hb ? { bcx: hb.dataset.bcx || '', pic: hb.classList.contains('bcpic'), stage: T.stage ? T.stage('rain', 9) : null } : null;
      F.close(); await sleep(200);
      return res;
    });
    // 第4弾：着せ替え。テーマを 切り替えて（解放の 確認は test_native）判定タブの 上の絵・色・字・テーマの 的中PUSH と ボードを 確かめる。
    //   第4.147版：桜を 外した ので 夕焼け（sunset：のこった「季節・行事」の 壁紙）で 確かめる
    // 見本の絵（ks_<id>.webp）は リポジトリに 入れないので、CIでは 404（なしでも 動く ことを 確かめる）。字（ks の WOFF2）と ks_<id>.json は 入っている
    await step(R, 'kisekae', async function () {
      var K = window.TengelKisekae; if (!K) return { on: false };
      await K.ready;
      var res = { list: K.list().length, groups: Array.from(new Set(K.list().map(function (t) { return t.group; }))), current0: K.current(), count: K.count(), usableSunset: K.usable('sunset'), usableGone: K.usable('sakura'), band: K.band, files: {} };
      for (var k of ['ks_sunset.json', 'ks_banner_ranch.svg', 'fonts/KaiseiOpti-700.woff2', 'ks_5f93d2cbb5295e4148858bf5daf03c5a.webp', 'ks_sakura.json']) { try { var r = await fetch(k, { cache: 'no-store' }); res.files[k] = r.status; } catch (e) { res.files[k] = String(e); } }
      await K.apply('sunset'); await sleep(900);
      document.querySelector('.tabbar [data-tab=judge]').click(); await sleep(400);
      var bn = document.querySelector('#ksBnr');
      res.sunset = { ks: document.documentElement.dataset.ks, loaded: K.loaded(), bnr: bn ? { hidden: bn.hidden, h: bn.getBoundingClientRect().height, w: bn.getBoundingClientRect().width, k: bn.style.getPropertyValue('--ksk'), anims: bn.getAnimations({ subtree: true }).length, inner: !!bn.querySelector('.ssw') } : null,
        bg: getComputedStyle(document.body).backgroundColor, font: getComputedStyle(document.body).fontFamily.slice(0, 40), hfont: getComputedStyle(document.querySelector('.brand h1')).fontFamily.slice(0, 30),
        fontLoaded: document.fonts.check('700 16px "Kaisei Opti"'), themeCss: !!document.querySelector('#ksTheme') && document.querySelector('#ksTheme').textContent.length, scrollW: document.documentElement.scrollWidth };
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
      // 第4.92版：壁紙パック（買い切り・10枚：第4.147版で 七夕を 外した）。いちばん 上の 組・買う 箱（買う 前）。絵の 部品（SVG）は アプリの 中に ある ので CI でも 動く（馬の コマと 止まった 絵は 404）
      if (K.pack) {
        var pk = K.pack();
        document.querySelector('.tabbar [data-tab=set]').click(); await sleep(400);
        var kc = document.querySelector('#setKisekae');
        res.pack = { ids: pk.ids, n: pk.ids.length, owned: pk.owned, first: kc && kc.querySelector('h3.ksg') ? kc.querySelector('h3.ksg').firstChild.textContent : null, buy: !!(kc && kc.querySelector('.kspk [data-ksact=pkbuy]')),
          usable: pk.ids.length ? K.usable(pk.ids[0]) : null };
        if (kc && kc.querySelector('.kspk')) { kc.querySelector('.kspk').scrollIntoView({ block: 'start' }); await sleep(300); }
        await mark('ks-pack');
        if (pk.ids.length) {
          await K.apply(pk.ids[0]); await sleep(900);
          document.querySelector('.tabbar [data-tab=judge]').click(); await sleep(500);
          var pb = document.querySelector('#ksBnr');
          res.pack.wall = { ks: document.documentElement.dataset.ks, anims: pb ? pb.getAnimations({ subtree: true }).length : -1, imgs: pb ? pb.querySelectorAll('img').length : -1, scrollW: document.documentElement.scrollWidth };
          await mark('ks-pack-wall');
        }
      }
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
        s1: d.s1, s5: d.s5, s10: d.s10, docs: d._docs, lines: d._lines, names: d.names || null };      // 第4.170版：names＝画像に 写って いた 馬の 名前（馬番ごと）
    });
    // 第4.172版（まさちゃん 11/14 22:05「やっぱりテンゲルBGMも消して！無しでいいや！」）：テンゲルBGM は なくした → しかけ（window.TengelBgm）と 設定の 札が 入って いない ことを 見る。
    //   ルーレットの 爆発の 動画（H.264 High：第4.171版）を この WebKit が 読める 形かも 見る
    await step(R, 'bgm', async function () {
      var v = document.createElement('video');
      return { has: !!window.TengelBgm, card: !!document.getElementById('setBgm'), h264: v.canPlayType('video/mp4; codecs="avc1.640032"') };
    });
    await step(R, 'wallet2', wallet);
    // App内課金：商品（シミュレーターでは App Store Connect の設定がないので、読めないことが多い。読めなくてもアプリは動く）
    await step(R, 'iap', async function () { return await TengelNative.iap('products'); });
    await step(R, 'layout', async function () { var L = await TengelNative.layout(); L.cssTop = getComputedStyle(document.documentElement).getPropertyValue('--top-inset'); L.cssBottom = getComputedStyle(document.documentElement).getPropertyValue('--bottom-inset'); L.padTop = getComputedStyle(document.documentElement).paddingTop; L.padBottom = getComputedStyle(document.documentElement).paddingBottom; return L; });
    // 第4.59版：上の帯の 所有ポイント（第4.139版：合計だけ「ポイント ○P」）・説明書は 札の 右（画面の 右はし）・iPad で 画面いっぱいなら 上に 24px（互換モードでは つかない）
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
    // 第4.155版：データの更新の ファイルを 開く 所（iOS に 入って いる 暗号＝CryptoKit の AES-GCM：DataSeal.swift）。ダミーの 鍵（0 が 32こ）で 封じた 見本（source/dataseal.py vector）を
    //   開けるか・1字 かえた 中身と ちがう 鍵は 開かないか（しるしが 合わない）。CI の ビルドは ダミーの 鍵なので、上の data（本物の 鍵で 封じた ファイル）は「形がちがう」に なるのが ふつう
    await step(R, 'unseal', async function () {
      var K = '00000000000000000000000000000000', IV = '77067561629ce0897e35a781', DATA = '0b4cdec4cf31574ac073ab3a1e6ae497d47d74702c772695bc216c04ac787a423066253967745906179406d8cf529616970718b144a33b162427f5c49ecbc6207351d8b8ff850201aa9e';
      var want = "{\"app\":\"tengel\",\"kind\":\"selftest\",\"msg\":\"テンゲル ok\"}";
      var open = function (k, iv, d) { return TengelNative.call('unseal', { key: k, iv: iv, data: d }).then(function (t) { return { ok: true, text: String(t) }; }, function (e) { return { ok: false, msg: String(e && e.message || e) }; }); };
      var good = await open(K, IV, DATA), bad = await open(K, IV, DATA.slice(0, -1) + (DATA.slice(-1) === '0' ? '1' : '0')), key2 = await open('00000000000000000000000000000001', IV, DATA), junk = await open(K, IV, 'zz');
      return { ok: good.ok && good.text === want && !bad.ok && !key2.ok && !junk.ok, good: good, bad: bad, key2: key2, junk: junk };
    });
    // 第4.123版：テンゲルデータ（1つ目）には 足せない・マザーデータ①〜③（2〜4つ目）と 名前
    await step(R, 'mother', function () { var L = TengelLocal.slots, r = L.rows(1).filter(function (x) { return x.src; }); return { n: L.rows(1).length, N: L.N, names: L.names(), fixed1: L.fixed(1), input: r.map(function (x) { return x.id + ' ' + x.p1 + '-' + x.p2 + '-' + x.p3; }), slots: L.info().map(function (s) { return s.n + ':' + s.count + (s.fixed ? ':fixed' : ''); }) }; });
    // 第4.123版：マザーデータの 入力用 Excel の ひな形が アプリの 中から 読める（Resources/mother_template.xlsx・zip の 頭は PK）
    await step(R, 'template', async function () { var r = await fetch('mother_template.xlsx'); var u = new Uint8Array(await r.arrayBuffer()); return { ok: r.ok, bytes: u.length, zip: u[0] === 0x50 && u[1] === 0x4b, share: typeof TengelNative.shareData === 'function' }; });
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
    // 第4.212版：値段（財布の 表）・おもちゃ・古い 台帳の リセットの カード
    try {
      var Wv = window.TengelWallet, oc = document.querySelector('#setOld'), bkc = document.querySelector('#setBackup');
      R.v212 = { cost: Wv ? Wv.COST : null, toys: Wv && Wv.toy ? Wv.toy.list() : null, toyItems: document.querySelectorAll('#setCustom .ptitem[data-key^="toy:"]').length, old: oc ? oc.innerText.slice(0, 400) : null, oldAfterBackup: !!(oc && bkc && bkc.nextElementSibling === oc),
        oldApi: typeof window.TengelOld, oldState: window.TengelOld ? window.TengelOld.state() : null, hist: Wv && Wv.old ? Wv.old.rows() : null, delBets: typeof (window.TengelLocal || {}).delBets };
    } catch (e) { R.v212 = { error: String(e) }; }
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
    // 第4.176版：馬カードバトル（cb/）を 本物の WebKit で：入口の ボタン（たてに 4つの 上から 3番目）・本体を 読む・コンピュータと さいごまで 対戦・ごほうび・アプリの 部屋の 窓口（Room.swift）の 返事
    await step(R, 'cb', async function () {
      // 右下の 丸い ボタン：順（order：上から トレーニングセンター → 推し馬 → カードバトル → 思い出フィギュア）・場所（たてに 1列＝col。たての 短い 画面 だけ 2列 × 2段＝g2）・丸の 大きさ（fd：画面に 合わせる）
      var ks = Array.prototype.slice.call(document.querySelectorAll('#fabCol > button')).sort(function (a, b) { return (+getComputedStyle(a).order) - (+getComputedStyle(b).order); });
      var rr = ks.map(function (k) { var r = k.getBoundingClientRect(); return [Math.round(r.left), Math.round(r.top), Math.round(r.right), Math.round(r.bottom)]; });
      var kb = document.getElementById('kiseBtn'), kr = kb ? kb.getBoundingClientRect() : null;
      var out = { fab: ks.map(function (k) { return k.id; }), fabRect: rr, kise: kr && kr.width ? [Math.round(kr.left), Math.round(kr.top), Math.round(kr.right), Math.round(kr.bottom)] : null, view: [window.innerWidth, window.innerHeight], api: typeof window.TengelCB };
      var under = function (a, b) { return a[3] <= b[1] + 1 && Math.abs((a[0] + a[2]) - (b[0] + b[2])) <= 4; }, fc = document.getElementById('fabCol');
      out.fd = ks.map(function (k) { var i = k.querySelector('.fabi'); return i ? Math.round(i.getBoundingClientRect().width) : 0; });
      out.col = rr.length === 4 && under(rr[0], rr[1]) && under(rr[1], rr[2]) && under(rr[2], rr[3]);
      out.g2 = !!fc && fc.classList.contains('g2') && rr.length === 4 && under(rr[0], rr[1]) && under(rr[2], rr[3]) && Math.abs(rr[2][1] - rr[0][1]) <= 1 && rr[2][0] >= rr[0][2] - 1;
      out.clear = !out.kise || rr.every(function (r) { return r[1] >= out.kise[3] + 2 || r[0] >= out.kise[2] || r[2] <= out.kise[0]; });      // 「壁紙&ボード着せ替え」に 重ならない（本物の 画面の 大きさで）
      if (!window.TengelCB) return out;
      out.room = await TengelNative.call('room', { op: 'state' }).catch(function (e) { return { error: String(e && (e.message || e)) }; });
      out.roomBad = await TengelNative.call('room', { op: 'join', room: '12a4' }).catch(function (e) { return { error: String(e && (e.message || e)) }; });
      // 第4.212版：TENGERカードバトルは おもちゃ（3,000P で 解放）。まだ 解放して いない → 丸い ボタンに 🔒・押すと 解放の 窓（カードバトルは 開かない）→「やめる」。
      //   その あと 解放ずみに して（openToys：ポイントは 使わない）開く
      try {
        var fabE = document.querySelector('#cbFab');
        out.toy = { locked: window.TengelCB.locked(), lock: !!(fabE && fabE.classList.contains('lock')), total: window.TengelWallet ? window.TengelWallet.total() : null };
        var opening = window.TengelCB.open();
        var tv = await waitFor(function () { return document.querySelector('#toyOv'); }, 8000);
        out.toy.ask = tv ? tv.innerText.replace(/\s+/g, ' ').slice(0, 140) : null;
        out.toy.btn = tv ? Array.prototype.map.call(tv.querySelectorAll('[data-toy]'), function (b) { return b.getAttribute('data-toy'); }).join() : null;
        out.toy.cbOpen = !!document.querySelector('#cbOv.on'); out.toy.bundle = !!window.CBApp;
        await mark('cb-toy');
        var nb = tv && tv.querySelector('[data-toy=no]'); if (nb) nb.click();
        await Promise.race([opening, sleep(3000)]); await sleep(200);
        out.toy.after = { ov: !!document.querySelector('#toyOv'), cb: !!document.querySelector('#cbOv.on') };
        out.toy.opened = await openToys(['cb']);
        out.toy.lock2 = !!(fabE && fabE.classList.contains('lock'));
      } catch (e) { out.toyErr = String(e && (e.message || e)); await openToys(['cb']).catch(function () {}); }
      await window.TengelCB.open();
      out.open = !!(await waitFor(function () { return window.CBApp && document.querySelector('#cbOv.on'); }, 20000));
      if (!out.open) return out;
      out.menu = Array.prototype.map.call(document.querySelectorAll('#cbOv .cbmenu .cbb'), function (b) { return b.textContent.replace(/\s+/g, ' ').trim(); });
      out.coinl = ((document.querySelector('#cbOv .cbmenu .cbcoinl') || {}).textContent || '');      // 第4.179版：バトルコインの 行
      out.gift0 = ((window.CBApp._t.state || {}).gifts || []).length; out.coin0 = (window.CBApp._t.state || {}).coin;      // 第4.188版：開いた とき もう 受け取って いた ログインボーナスの バトルコイン（毎日 2枚）
      out.roomBtn = Array.prototype.map.call(document.querySelectorAll('#cbOv .cbmenu [data-cb=host],#cbOv .cbmenu [data-cb=join]'), function (b) { return !b.disabled; });
      await mark('cb-menu');
      window.CBApp._t.speed(0.2); window.CBApp._think = function () { return 200; };
      document.querySelector('#cbOv .cbmenu [data-cb=cpu]').click();
      await waitFor(function () { return window.CBApp._t.view && window.CBApp._t.idle; }, 20000);
      await sleep(700);
      var v0 = window.CBApp._t.view; out.start = v0 ? { hand: v0.my.hand.length, op: v0.op.hand.length, deck: v0.deckN, turn: v0.turn, turns: v0.turns } : null;
      // 第4.178版：設定（BGM・効果音・エフェクト）の はじめの 形・夜の フィールドの 火の あかり（.cbfire の ゆれ）・BGM（CI の ビルドには 音の ファイルが ない → 鳴らさずに そのまま 進む）
      // 第4.185版：設定は BGM・効果音 だけ（エフェクトは なくした：sets に fx が ない・窓に エフェクトの ボタンが ない）・プレイボードは いつもの 絵（cb_board.webp：cust なし）
      try {
        var se0 = window.CBApp._t.sets, bg0 = window.CBApp._t.bgm;
        out.sets = { bgm: se0.bgm, se: se0.se, fx: 'fx' in se0, as: se0.as };
        out.bgm = { on: bg0.on, want: bg0.want, gone: bg0.gone, len: Math.round(bg0.len * 100) / 100, ctx: bg0.ctx };
        out.fire = Array.prototype.map.call(document.querySelectorAll('#cbOv .cbfire'), function (e) { var c = getComputedStyle(e); return c.animationName + ' ' + c.animationDuration; });
        document.querySelector('#cbOv .cbgear').click(); await sleep(200);
        out.gear = Array.prototype.map.call(document.querySelectorAll('#cbOv .cbmod.cbset .cbsw'), function (r) { return r.getAttribute('data-set'); }).join();
        out.fxBtn = !!document.querySelector('#cbOv .cbset [data-k=fx]');
        var bdi = document.querySelector('#cbOv .cbboard > img'); out.board = bdi ? [bdi.getAttribute('src'), document.querySelector('#cbOv .cbboard').classList.contains('cust')] : null;
        var mx = document.querySelector('#cbOv .cbset [data-cb=modx]'); if (mx) mx.click(); await sleep(200);
      } catch (e) { out.setsErr = String(e); }
      await mark('cb-game');
      out.auto = await cbAuto(150000);
      var v = window.CBApp._t.view; out.res = v ? v.res : null; out.wins = v ? [v.my.wins, v.op.wins] : null; out.discard = v ? v.discard.length : null; out.early = v ? v.early || 0 : null;      // 第4.202版：決着で おわった ターン（0＝さいごまで）
      out.gift = await waitFor(function () { var e = document.querySelector('#cbOv .cbend .gift'); return e && e.textContent.length > 3 ? e.textContent : null; }, 20000);
      out.state = JSON.parse(JSON.stringify(window.CBApp._t.state)); out.tokens = window.TCApp && window.TCApp.state ? window.TCApp.state.stock : null;
      await mark('cb-end');
      var mb = document.querySelector('#cbOv .cbend [data-cb=menu]'); if (mb) mb.click(); await sleep(300);
      var cl = document.querySelector('#cbOv .cbmenu [data-cb=close]'); if (cl) cl.click(); await sleep(300);
      out.closed = !document.querySelector('#cbOv.on');
      return out;
    });
    // 第4.177版：お世話の 札の「描く 命令を 書きとめる 役」（tc/tc_care.js の REC：同じ 絵の コマは 紙に さわらない）を 本物の WebKit で たしかめる。
    //   トレーニングセンターの 絵と 3D は この ビルドに 入って いない ので 開かない。部品 だけ 読んで（tc_bundle.js）、ためしの 紙に いろいろな 命令（ぬり・線・字・色の ぼかし・影・切りぬき・足す 光・点線・絵）を
    //   書きとめ役を 通して 描き、同じ 命令を じかに 描いた 紙と 1画素ずつ くらべる（REC.check）。同じ 絵が つづく コマ・かくれて いる コマは 描かない ことも 数える
    await step(R, 'hudrec', async function () {
      var out = { have: false };
      if (!window.TCCare) { await new Promise(function (r) { var sc = document.createElement('script'); sc.src = 'tc_bundle.js'; sc.onload = r; sc.onerror = r; document.head.appendChild(sc); }); await sleep(200); }
      var REC = window.TCCare && window.TCCare.REC; if (!REC) return out;
      out.have = true; out.ok0 = REC.ok; if (!REC.ok) return out;
      var cv = document.createElement('canvas'); cv.width = 240; cv.height = 160; var g0 = cv.getContext('2d');
      var img = document.createElement('canvas'); img.width = 40; img.height = 40; img._fix = true;      // _fix＝中身の かわらない 紙
      var ig = img.getContext('2d'); ig.fillStyle = '#c33'; ig.fillRect(0, 0, 40, 40); ig.fillStyle = '#fc6'; ig.beginPath(); ig.arc(20, 20, 14, 0, 6.2832); ig.fill();
      var mut = document.createElement('canvas'); mut.width = 30; mut.height = 30; var mg = mut.getContext('2d'); mg.fillStyle = '#2a6'; mg.fillRect(0, 0, 30, 30);      // あとから 中身の かわる 紙
      var lg = g0.createLinearGradient(0, 0, 0, 100); lg.addColorStop(0, 'rgba(255,240,200,0.9)'); lg.addColorStop(1, 'rgba(200,120,60,0.6)');
      var rg = g0.createRadialGradient(120, 40, 2, 120, 40, 30); rg.addColorStop(0, 'rgba(120,255,160,0.8)'); rg.addColorStop(1, 'rgba(120,255,160,0)');
      var reads = [];
      function scene(g, k) {
        g.setTransform(1, 0, 0, 1, 0, 0); g.clearRect(0, 0, 240, 160); g.setTransform(1.5, 0, 0, 1.5, 0, 0);
        g.lineJoin = 'round'; g.lineCap = 'round';
        g.fillStyle = lg; g.beginPath(); g.moveTo(10, 10); g.lineTo(90, 14); g.quadraticCurveTo(100, 40, 80, 60); g.bezierCurveTo(60, 70, 30, 66, 12, 50); g.closePath(); g.fill();
        g.strokeStyle = '#5a3a1a'; g.lineWidth = 2 + k; g.lineWidth = -3; reads.push(g.lineWidth); g.stroke();      // だめな 値（−3）は 本物と 同じく 捨てる
        g.save(); g.shadowColor = 'rgba(0,0,0,0.5)'; g.shadowBlur = 4; g.shadowOffsetY = 2; g.font = '700 14px sans-serif'; g.textAlign = 'center'; g.textBaseline = 'middle';
        var w = g.measureText('お世話 ' + k).width; g.fillStyle = '#fff8ea'; g.fillRect(50 - w / 2 - 4, 26, w + 8, 20); g.restore();
        g.font = '700 14px sans-serif'; g.textAlign = 'center'; g.textBaseline = 'middle'; g.fillStyle = '#c2362b'; g.strokeStyle = '#fff'; g.lineWidth = 3; g.strokeText('お世話 ' + k, 50, 36); g.fillText('お世話 ' + k, 50, 36);
        g.save(); g.beginPath(); g.arc(120, 40, 26, 0, 6.2832); g.clip(); g.globalCompositeOperation = 'lighter'; g.fillStyle = rg; g.fillRect(90, 10, 60, 60);
        g.globalAlpha = 0.75; g.globalAlpha = g.globalAlpha * 0.5; reads.push(g.globalAlpha); g.fillStyle = '#48f'; g.fillRect(100 + k * 3, 20, 20, 40); g.restore();
        g.save(); g.translate(40, 85); g.rotate(0.2 * k); g.setLineDash([4, 3]); g.lineDashOffset = k; g.strokeStyle = '#264'; g.lineWidth = 1.5; g.strokeRect(-20, -10, 40, 20); g.setLineDash([]); g.restore();
        g.drawImage(img, 100, 70); g.drawImage(img, 5, 5, 30, 30, 70, 76, 20, 20); g.globalAlpha = 0.7; g.drawImage(img, 126, 72, 24, 24); g.globalAlpha = 1;
        if (k === 3) g.drawImage(mut, 4, 70);
      }
      var st0 = JSON.parse(JSON.stringify(REC.stat));
      REC.check(true);
      var seq = [0, 0, 0, 1, 1, 2, 2, 2, 0, 0, 3, 3], i, g;
      for (i = 0; i < seq.length; i++) {
        if (i === 11) { mg.fillStyle = '#a2c'; mg.fillRect(6, 6, 18, 18); }      // 中身を かえた：次の コマに 出る
        g = REC.begin(g0, false); scene(g, seq[i]); REC.end();
      }
      for (i = 0; i < 2; i++) { g = REC.begin(g0, true); scene(g, 1); REC.end(); }      // かくれて いる コマ（描かない）
      for (i = 0; i < 2; i++) { g = REC.begin(g0, false); scene(g, 1); REC.end(); }     // 出て きた：1コマ目は 描く・2コマ目は 同じ
      var st = REC.stat; out.stat = { frames: st.frames - st0.frames, drawn: st.drawn - st0.drawn, same: st.same - st0.same, hidden: st.hidden - st0.hidden, forced: st.forced - st0.forced, bad: st.bad - st0.bad };
      out.checks = REC.checks; out.notes = st.notes.slice(0, 4); out.ok1 = REC.ok;
      REC.check(false); REC.resync();
      out.reads = [reads[0], reads[1], reads.length];      // 読んだ 値：線の 太さ（−3 を 捨てて 2）・こさ（0.75 × 0.5＝0.375）・読んだ 回数（16コマ × 2）
      // べつの たしかめ：同じ 場面を 新しい 紙に じかに 描いて、書きとめ役を 通した 紙と くらべる
      var ref = document.createElement('canvas'); ref.width = 240; ref.height = 160; scene(ref.getContext('2d'), 1);
      var a = g0.getImageData(0, 0, 240, 160).data, b = ref.getContext('2d').getImageData(0, 0, 240, 160).data, df = 0, px = 0;
      for (i = 0; i < a.length; i += 4) { if (a[i] !== b[i] || a[i + 1] !== b[i + 1] || a[i + 2] !== b[i + 2] || a[i + 3] !== b[i + 3]) df++; if (a[i + 3] > 0) px++; }
      out.diff = df; out.px = +(px / (a.length / 4)).toFixed(3);
      out.names = Object.getOwnPropertyNames(CanvasRenderingContext2D.prototype).length;
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
    await step(R, 'clock', clock);      // 第4.191版
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
  // 第4.156版：iPad の 広い 窓（Swift Playgrounds の ▶ と 同じ）→ Webの 画面は 390×844（まわりは 黒）・時計の 帯の あきは 0・壁紙は 引きのばさない（--ksk 1）
  async function phase4() {
    await ready();
    var R = { phase: 4, device: DEV };
    R.basic = basic();
    await step(R, 'layout', async function () { var L = await TengelNative.layout(); L.cssTop = getComputedStyle(document.documentElement).getPropertyValue('--top-inset'); L.cssBottom = getComputedStyle(document.documentElement).getPropertyValue('--bottom-inset'); return L; });
    await step(R, 'screen', function () { return { w: screen.width, h: screen.height, iw: innerWidth, ih: innerHeight, dpr: devicePixelRatio, topInset2: document.documentElement.style.getPropertyValue('--top-inset2') }; });
    tab('judge'); await sleep(900);
    await step(R, 'banner', function () { var b = document.querySelector('#ksBnr'); if (!b) return null; var r = b.getBoundingClientRect(); return { hidden: b.hidden, w: r.width, h: r.height, k: b.style.getPropertyValue('--ksk'), ks: document.documentElement.dataset.ks || '' }; });
    await step(R, 'header', function () { var h = document.querySelector('header.top'); if (!h) return null; var r = h.getBoundingClientRect(); return { top: r.top, w: r.width }; });
    await mark('wide-main');
    report('4', R);
  }
  // 第4.169版（まさちゃん 2026/11/14「テスト版のみに全てをリセットできる機能つけて！」）：テスト版の「ぜんぶ リセット」を 本物の WKWebView で 確かめる。
  //   1ページ目（まだ 消して いない＝TengelReset.did() が null）：記録・設定・端末の おぼえを 作る → 設定の「テスト版の道具」→「ぜんぶ リセット」→「リセット する」→ ページが 開き直る
  //   2ページ目（消した あと）：保存場所（IndexedDB）を 消し おわったか・記録 0件・設定なし・端末の おぼえなし・「はじめる」の 画面・「前の記録が見つかったよ」が 出ない・作り直した 保存場所に 書ける
  //   （キーチェーンの しるしは シミュレーターでは 読めない〈error:-34018〉ので ここでは 見ない）
  async function phase5() {
    var RS = window.TengelReset, did = RS && RS.did();
    if (!did) {
      await ready();
      var R = { phase: 5, device: DEV, page: 'before', hasReset: !!RS, test: window.__TEST === true };
      R.basic = basic();
      await step(R, 'seed', async function () {
        await TengelLocal.putBets([{ id: 'st5-bet', date: '2026-11-08', venue: '', r: 9, rname: 'リセットの ためし', n: 14, types: ['馬単'], n1: 8, n2: 4, n3: 6, p1: 3, p2: 1, p3: 2, stake: '600', payout: '0', horses: [],
          rsv: { state: 'done', types: ['馬単'], bets: { '馬単': [[3, 7], [7, 3]] }, result: { p: [[8], [4], [6]] }, fx: 'miss', at: new Date().toISOString() } }]);
        await TengelLocal.putSetting('st5', 'x');
        localStorage.setItem('tengel.st5', '1'); sessionStorage.setItem('st5', '1');
        return true;
      });
      await sleep(2600);   // 自動バックアップ（保存の 1.5秒 あと）
      await step(R, 'before', async function () {
        var s = await TengelNative.loadBackup(), W = window.TengelWallet;
        return { bets: TengelLocal.mem.bets.size, setting: await TengelLocal.getSetting('st5'), ls: Object.keys(localStorage).sort(), ss: Object.keys(sessionStorage).sort(), total: W ? W.total() : null,
          events: W ? W.events().map(function (e) { return e.id + ':' + e.amount; }) : null, backup: s ? { n: (s.bets || []).length, at: s.at || null } : null, gate: window.__gate };
      });
      var lg = document.querySelector('#lgOv [data-lg=ok]'); if (lg) { lg.click(); await sleep(400); }   // ログインボーナスの 窓が 出て いたら とじる
      tab('set'); await sleep(800);
      var b1 = document.querySelector('#setTest [data-test=wipe]');
      R.card = { card: !!document.querySelector('#setTest'), btn: !!b1 };
      if (b1) { b1.click(); await sleep(900); }   // 1回目：まん中に たしかめる 窓（出て から 0.7秒は「リセット する」を 受けない）
      var w = document.querySelector('#testWipe'), bx = w && w.querySelector('.twbox');
      R.confirm = w ? { hidden: w.hidden, text: w.innerText.slice(0, 60), rect: (function (r) { return [Math.round(r.left), Math.round(r.top), Math.round(r.width), Math.round(r.height)]; })((bx || w).getBoundingClientRect()), iw: innerWidth, ih: innerHeight,
        z: getComputedStyle(w).zIndex, mark: localStorage.getItem('tengel.wipe') } : null;
      await mark('reset-confirm');
      report('5a', R);
      await sleep(400);
      var go = document.querySelector('#testWipe [data-test=wipego]');
      if (go) go.click();   // 2回目：画面を かくして 開き直す → 2ページ目へ
      else report('5', { phase: 5, device: DEV, page: 'after', failed: 'リセットの ボタンが ない' });
      return;
    }
    var R2 = { phase: 5, device: DEV, page: 'after', did0: JSON.parse(JSON.stringify(did)) };
    await loaded();
    R2.db = await waitFor(function () { var d = window.TengelReset.did(); return d.db !== 'pending' && d.db !== 'blocked' ? d.db : null; }, 20000) || window.TengelReset.did().db;
    await waitFor(function () { return window.TengelLocal; }, 20000);
    await window.TengelLocal.ready.catch(function () {});
    if (window.TengelWallet) await window.TengelWallet.ready;
    await sleep(1500);   // 「前の記録が見つかったよ」が 出る なら この ころ（保存場所が 読めて すぐ）
    var g = document.querySelector('#gate');
    R2.gate = { shown: !!(g && !g.hidden), first: !!document.querySelector('#gateGo'), note: (document.querySelector('#wipeNote') || {}).textContent || null };
    await mark('reset-gate');
    await step(R2, 'after', async function () {
      var s = await TengelNative.loadBackup(), W = window.TengelWallet, st = await TengelLocal.getSetting('st5');
      return { did: window.TengelReset.did(), bets: TengelLocal.mem.bets.size, races: TengelLocal.mem.races.size, memOnly: TengelLocal.memOnly(), setting: st === undefined ? null : st,
        ls: Object.keys(localStorage).sort(), ss: Object.keys(sessionStorage).sort(), total: W ? W.total() : null, events: W ? W.events().map(function (e) { return e.id + ':' + e.amount; }) : null,
        offer: !!document.querySelector('#nativeRestore'), backup: s ? { n: (s.bets || []).length, at: s.at || null, reset: !!s.reset, auto: !!s.auto } : null };
    });
    await step(R2, 'write', async function () { await TengelLocal.putSetting('st5b', 7); return await TengelLocal.getSetting('st5b'); });   // 作り直した 保存場所に 書ける
    window.__gate = await gate(false);
    await sleep(1800);
    R2.main = { gate: window.__gate, tabbar: !!document.querySelector('.tabbar'), login: !!document.querySelector('#lgOv'), offer: !!document.querySelector('#nativeRestore'), total: window.TengelWallet ? window.TengelWallet.total() : null };
    await mark('reset-main');
    await sleep(1800);
    await step(R2, 'backupAfter', async function () { var s = await TengelNative.loadBackup(); return s ? { n: (s.bets || []).length, auto: !!s.auto, reset: !!s.reset, wallet: s.wallet && s.wallet.events ? s.wallet.events.length : 0 } : null; });
    report('5', R2);
  }
  // 馬カードバトルを 自動で 進める（番が 来たら 押す：効果は 使わない・手札の 左から 出す）。対戦が 終わる か ms たつ まで。返り値＝押した 回数 など
  async function cbAuto(ms) {
    var T = window.CBApp._t, t0 = Date.now(), n = 0, kinds = {};
    var click = function (sel) { var e = document.querySelector(sel); if (e && !e.disabled) { e.click(); return true; } return false; };
    while (Date.now() - t0 < ms && !T.ended && T.match) {
      if (T.idle && T.view) {
        var v = T.view, s = v.pend && v.pend.mine ? v.pend.type : v.can.six ? 'six' : v.can.eff ? 'eff' : v.can.set ? ((v.can.x7r || v.can.x7 || v.can.x3) && T.ask ? 'x7' : 'set') : 'wait';
        if (s === 'x7') { if (click('#cbOv .cbask [data-cb=x7no]') || click('#cbOv .cbask [data-cb=p7no]') || click('#cbOv .cbask [data-cb=p3no]')) { n++; kinds.x7 = (kinds.x7 || 0) + 1; } }      // 第4.187版：7 が 4まい・第4.202版：7 が 3まい・3 が 3まい（セットの 前）→ 使わない
        else if (s === 'k' || s === 'm') { if (click('#cbOv [data-cb=' + s + 'skip]')) { n++; kinds[s] = (kinds[s] || 0) + 1; } }
        else if (s === 'rev') { if (click('#cbOv [data-cb=revyes]')) { n++; kinds.rev = (kinds.rev || 0) + 1; } }      // 第4.178版：逆転勝利（1・2 の 効果）を 聞かれたら 使う
        else if (s === 'u5') { if (click('#cbOv [data-cb=u5no]')) { n++; kinds.u5 = (kinds.u5 || 0) + 1; } }      // 第4.183版：4 の 効果で 交換して 5 を 出した → 5 の 効果は 使わない
        else if (s === 'six') { if (click('#cbOv [data-cb=sixno]')) { n++; kinds.six = (kinds.six || 0) + 1; } }      // 第4.190版：ターンの はじめの 6 の 効果 → 使わない
        else if (s === 'eff') { if (click('#cbOv [data-cb=effno]') || click('#cbOv .cbact [data-cb=effback]')) { n++; kinds.eff = (kinds.eff || 0) + 1; } }      // 効果タイム（2人とも セットした あと）：使わない
        else if (s === 'swap' || s === 'set') {
          if (!T.modOn()) click('#cbOv .cbhand .cbc');
          await sleep(120);
          if (click('#cbOv .cbmod [data-cb=' + s + ']')) { n++; kinds[s] = (kinds[s] || 0) + 1; }
        }
      }
      await sleep(150);
    }
    return { clicks: n, kinds: kinds, ended: !!T.ended, ms: Date.now() - t0 };
  }
  // 6回目（部屋を 作る）・7回目（部屋に 入る）：2台の シミュレーターで 対戦
  async function phaseRoom(host) {
    var R = { phase: PH, device: DEV, host: host, room: String(window.__ST_ROOM || ''), evs: [] };
    document.addEventListener('tengel:native', function (e) { var d = e.detail || {}; if (d.name !== 'room') return; var p = d.payload || {}; R.evs.push(p.ev === 'data' ? 'data' : p.ev + ':' + (p.state || p.why || '')); });
    await loaded();
    window.__gate = await gate(false);
    await waitFor(function () { return window.TengelCB && document.querySelector('#cbFab'); }, 20000);
    R.api = typeof window.TengelCB;
    if (!window.TengelCB) { report(String(PH), R); return; }
    R.toy = await openToys(['cb']).catch(function (e) { return String(e); });      // 第4.212版：TENGERカードバトルは おもちゃ（3,000P で 解放）→ 解放ずみに して 開く
    await window.TengelCB.open();
    R.open = !!(await waitFor(function () { return window.CBApp && document.querySelector('#cbOv.on'); }, 20000));
    if (!R.open) { report(String(PH), R); return; }
    window.CBApp._t.speed(0.2);
    if (host) {
      window.CBApp._room = R.room; document.querySelector('#cbOv .cbmenu [data-cb=host]').click(); await sleep(300);
      var sg = document.querySelector('#cbOv .cbroom [data-cb=stkgo]'); R.stakeStep = !!sg; if (sg) sg.click();      // 第4.179版：バトルコインを 持って いれば 参加コインを 決める 画面 → コインなしで 作る
    }
    else {
      document.querySelector('#cbOv .cbmenu [data-cb=join]').click(); await sleep(300);
      for (var i = 0; i < R.room.length; i++) { var k = document.querySelector('#cbOv .cbkeys [data-key="' + R.room.charAt(i) + '"]'); if (k) k.click(); await sleep(80); }
      var go = document.querySelector('#cbOv .cbkeys [data-key=go]'); R.go = !!(go && !go.disabled); if (go) go.click();
    }
    await sleep(500);
    R.shown = (document.querySelector('#cbOv .cbroom .num') || {}).textContent || '';
    R.connected = !!(await waitFor(function () { return window.CBApp._t.screen === 'game' && window.CBApp._t.view ? true : null; }, 240000));      // 第4.190版：2分 → 4分（run 157 の macOS 26 は iPad が つながるのに 2分 より かかった）
    R.screen = window.CBApp._t.screen;
    if (!R.connected) { R.text = ((document.querySelector('#cbOv .cbroom') || {}).textContent || '').slice(0, 240); R.evs = R.evs.slice(0, 60); report(String(PH), R); return; }
    R.kind = window.CBApp._t.match ? window.CBApp._t.match.kind : null;
    R.auto = await cbAuto(150000);
    var v = window.CBApp._t.view; R.res = v ? v.res : null; R.wins = v ? [v.my.wins, v.op.wins] : null; R.discard = v ? v.discard.length : null; R.early = v ? v.early || 0 : null;
    R.gift = await waitFor(function () { var e = document.querySelector('#cbOv .cbend .gift'); return e && e.textContent.length > 3 ? e.textContent : null; }, 15000);
    R.evs = R.evs.filter(function (x) { return x !== 'data'; }).concat(['data×' + R.evs.filter(function (x) { return x === 'data'; }).length]);
    report(String(PH), R);
  }
  var run = isManual ? manualPage : PH === 2 ? phase2 : PH === 3 ? phase3 : PH === 4 ? phase4 : PH === 5 ? phase5 : PH === 6 ? function () { return phaseRoom(true); } : PH === 7 ? function () { return phaseRoom(false); } : phase1;
  run().catch(function (e) { report('crash-' + (isManual ? 'manual' : PH), { phase: PH, device: DEV, exception: String(e && (e.stack || e.message || e)) }); });
})();
