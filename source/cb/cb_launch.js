// 馬カードバトルの 入口（App Store版だけ・index.html の 中に 入る 小さい 部分）：第4.176版（まさちゃん 2026/11/15 21:41「TENGER馬カードバトル …アイコンは推し馬の上に設置して！」）
//   ・名前（画面に 出す）：「TENGERカードバトル」（11/16 01:16 まさちゃん「カードバトルを、TENGERカードバトルに名前変えて！」。ボタンの 札は 2行「TENGER／カードバトル」）
//   ・右下の 丸い ボタンの 列（#fabCol：tc/tc_launch.js の TengelFab）に 丸い ボタン（#cbFab・絵 cb_icon.webp＝まさちゃんの アイコン・下に 名前「カードバトル」）
//     場所：はじめは 列の 1番 上（推し馬の 上）→ 11/16 00:47 まさちゃん「トレーニングセンターを一番上、カードバトルを思い出フィギュアの上にして
//       ①トレーニングセンター ②推し馬 ③カードバトル ④思い出フィギュア」＝ 上から 3番目（推し馬の 下・思い出フィギュアの 上）
//   ・押した ときに cb_bundle.js（ルール・コンピュータ・対戦の 進め役・画面）を 読んで CBApp.open()。絵と 音は build_ios.py が Resources/ に 入れる（リポジトリには 入れない）
(function () {
  'use strict';
  if (!window.__NATIVE) return;
  var loading = null, fab = null;
  function note(m) { try { var t = document.getElementById('toast'); if (t) { t.textContent = m; t.hidden = false; clearTimeout(t._tc); t._tc = setTimeout(function () { t.hidden = true; }, 4200); } } catch (e) { /* なし */ } }
  function load() {
    if (window.CBApp) return Promise.resolve();
    if (!loading) loading = new Promise(function (ok, ng) { var s = document.createElement('script'); s.src = 'cb_bundle.js'; s.onload = function () { ok(); }; s.onerror = function () { loading = null; ng(new Error('load')); }; document.head.appendChild(s); });
    return loading;
  }
  // 第4.212版（まさちゃん 2026/11/23 10:12「⑤おもちゃを購入を追加 パチンコとテンゲルカードバトルとポイント解放型にして、3000Pで解放にする！」・答え「1つずつ 3,000P」）：
  //   TENGERカードバトルは「おもちゃ」（Pカスタムで 解放・3,000P：points.js の TOYS・COST.toy）。まだ 解放して いない ときは 丸い ボタンに 🔒・
  //   押すと 解放の 窓（points_ui.js の TengelWallet.toy.ask：「3,000Pを使って解放する」「やめる」・足りない ときは「ポイントを買う」）→ 解放 できたら 開く
  function toy() { var w = window.TengelWallet; return w && w.on && w.toy ? w.toy : null; }
  function locked() { var t = toy(); return !!t && !t.has('cb'); }
  function gate() {
    var t = toy(); if (!t) return Promise.resolve(true);
    return Promise.resolve(window.TengelWallet.ready).then(function () { return t.has('cb') ? true : t.ask('cb'); });
  }
  function paintLock() {
    if (!fab) return;
    if (!document.getElementById('cbLockCss')) {
      var st = document.createElement('style'); st.id = 'cbLockCss';
      st.textContent = '#cbFab.lock{position:relative}#cbFab.lock::before{content:"🔒";position:absolute;right:-1px;top:-5px;z-index:1;font-size:15px;line-height:1;filter:drop-shadow(0 1px 1.5px rgba(0,0,0,.6));pointer-events:none}';
      document.head.appendChild(st);
    }
    var on = locked(); fab.classList.toggle('lock', on);
    fab.setAttribute('aria-label', on ? 'TENGERカードバトル（おもちゃ：ポイントで 解放すると 遊べるよ）' : 'TENGERカードバトル（押すと 開くよ）');
  }
  function open() {
    if (fab) fab.disabled = true;
    return gate().then(function (ok) {
      if (!ok) return null;
      return load().then(function () { return window.CBApp.open(); }).catch(function () { note('TENGERカードバトルを 読みこめなかったよ。もう一度 押してね'); });
    }).catch(function () { /* 解放の 窓が 出せなかった：何も しない */ }).then(function () { if (fab) fab.disabled = false; paintLock(); });
  }
  window.TengelCB = { open: open, locked: locked };
  function boot() {
    if (document.getElementById('cbFab') || !window.TengelFab) return;
    fab = window.TengelFab.add({ id: 'cbFab', order: 2, name: ['TENGER', 'カードバトル'], aria: 'TENGERカードバトル（押すと 開くよ）', img: 'cb_icon.webp', fb: ['バトル', '#0F3A1E', '#E2B33C', '#FFE6A0'], tap: open });
    paintLock();
    try { Promise.resolve(window.TengelWallet && window.TengelWallet.ready).then(paintLock, function () { }); } catch (e) { /* なし */ }
    document.addEventListener('tengel:wallet', paintLock);      // 解放した（Pカスタムの カードから でも）→ 🔒 を 消す
  }
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', boot); else boot();
})();
